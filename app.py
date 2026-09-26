"""
=============================================================================
CKD Stage Prediction Pipeline - Flask Backend REST API with SQLite Integration
=============================================================================
This Flask application serves the Stacked Ensemble (Random Forest + XGBoost) 
model for Chronic Kidney Disease (CKD) stage prediction and persists prediction
history to a SQLite database (ckd_database.db).

Endpoints:
  - GET  /                : Serves index.html UI
  - GET  /predict.html    : Serves predict.html UI
  - GET  /results.html    : Serves results.html UI
  - GET  /health          : Health check endpoint returning {"status": "ok"}
  - POST /predict         : Predicts CKD stage and saves record to SQLite database
  - GET  /history         : Retrieves prediction history (ordered most recent first)
  - GET  /patient/<id>    : Retrieves diagnostic history for a specific patient
=============================================================================
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
import sqlite3
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")

DB_FILE = os.path.join(os.path.dirname(__file__), "ckd_database.db")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

# Directory paths for saved model artifacts
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# Global variables for loaded models & encoders
rf_model = None
xgb_model = None
le_gender = None
le_ethnicity = None
le_target = None
meta = None

REQUIRED_FIELDS = [
    'age', 'gender', 'ethnicity', 'education_level', 'poverty_income_ratio', 
    'bmi', 'weight_kg', 'height_cm', 'bp_systolic', 'bp_diastolic', 
    'blood_urea_nitrogen', 'albumin_serum', 'phosphorus', 'bicarbonate', 
    'calcium', 'uric_acid', 'urine_creatinine', 'urine_albumin', 
    'albumin_creatinine_ratio', 'diabetes_diagnosed', 'insulin_use', 
    'diabetes_pills', 'ever_smoked', 'current_smoker'
]

# Alert Threshold Constants for Patient Health Monitoring & Deterioration Alerts
BP_INCREASE_THRESHOLD = 15.0  # Systolic or Diastolic blood pressure increase (mmHg)
BUN_INCREASE_THRESHOLD = 5.0  # Blood Urea Nitrogen increase (mg/dL)
ACR_INCREASE_THRESHOLD = 30.0 # Albumin-Creatinine Ratio increase (mg/g)

STAGE_SEVERITY_MAP = {
    "No CKD": 0,
    "Stage 1 (Kidney Damage)": 1,
    "Stage 2 (Mildly Decreased)": 2,
    "Stage 3a (Mild-Moderate)": 3,
    "Stage 3b (Moderate-Severe)": 4,
    "Stage 4 (Severely Decreased)": 5,
    "Stage 5 (Kidney Failure)": 6
}

def evaluate_patient_alerts(predictions):
    """
    Compares the most recent record against the previous record (chronologically sorted oldest to newest).
    Returns list of alert dictionaries: [{"type": "...", "message": "..."}]
    """
    alerts = []
    if len(predictions) < 2:
        return alerts

    prev = predictions[-2]
    curr = predictions[-1]

    # 1. CKD Stage Progression Alert
    prev_stage_val = STAGE_SEVERITY_MAP.get(prev.get('predicted_stage', ''), 0)
    curr_stage_val = STAGE_SEVERITY_MAP.get(curr.get('predicted_stage', ''), 0)
    if curr_stage_val > prev_stage_val:
        alerts.append({
            "type": "Stage Progression Alert",
            "message": f"Stage worsened from {prev.get('predicted_stage', 'Unknown')} to {curr.get('predicted_stage', 'Unknown')} since last visit."
        })

    # 2. Blood Pressure Alert
    prev_sys = float(prev.get('bp_systolic', 0))
    curr_sys = float(curr.get('bp_systolic', 0))
    prev_dia = float(prev.get('bp_diastolic', 0))
    curr_dia = float(curr.get('bp_diastolic', 0))
    sys_diff = curr_sys - prev_sys
    dia_diff = curr_dia - prev_dia

    if sys_diff > BP_INCREASE_THRESHOLD or dia_diff > BP_INCREASE_THRESHOLD:
        bp_details = []
        if sys_diff > BP_INCREASE_THRESHOLD:
            bp_details.append(f"Systolic BP increased by {sys_diff:.1f} mmHg ({prev_sys:.0f} → {curr_sys:.0f})")
        if dia_diff > BP_INCREASE_THRESHOLD:
            bp_details.append(f"Diastolic BP increased by {dia_diff:.1f} mmHg ({prev_dia:.0f} → {curr_dia:.0f})")
        alerts.append({
            "type": "Blood Pressure Alert",
            "message": f"Significant blood pressure increase: {'; '.join(bp_details)}."
        })

    # 3. Lab Value Alert (BUN or ACR)
    prev_bun = float(prev.get('blood_urea_nitrogen', 0))
    curr_bun = float(curr.get('blood_urea_nitrogen', 0))
    prev_acr = float(prev.get('albumin_creatinine_ratio', 0))
    curr_acr = float(curr.get('albumin_creatinine_ratio', 0))
    bun_diff = curr_bun - prev_bun
    acr_diff = curr_acr - prev_acr

    lab_details = []
    if bun_diff > BUN_INCREASE_THRESHOLD:
        lab_details.append(f"Blood Urea Nitrogen increased by {bun_diff:.1f} mg/dL ({prev_bun:.1f} → {curr_bun:.1f})")
    if acr_diff > ACR_INCREASE_THRESHOLD:
        lab_details.append(f"Albumin-Creatinine Ratio increased by {acr_diff:.1f} mg/g ({prev_acr:.1f} → {curr_acr:.1f})")

    if lab_details:
        alerts.append({
            "type": "Lab Value Alert",
            "message": f"Concerning lab value changes: {'; '.join(lab_details)}."
        })

    return alerts


def init_db():
    """Initializes the SQLite database using schema.sql if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_FILE)
        with open(SCHEMA_FILE, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print(f"[INFO] Database initialized at {DB_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")

def get_db_connection():
    """Establishes connection to SQLite database. Returns None gracefully if offline."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=3)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as err:
        print(f"[WARNING] SQLite Connection Failed: {err}")
        return None

def save_prediction_to_db(input_data, raw_input, predicted_stage, confidence, probabilities):
    """Saves prediction record into SQLite database without failing prediction request."""
    conn = get_db_connection()
    if not conn:
        print("[WARNING] Database offline. Prediction calculated but not saved to SQLite.")
        return None

    try:
        cursor = conn.cursor()
        
        patient_id = raw_input.get("patient_id")
        patient_name = raw_input.get("patient_name", "Anonymous Patient")

        if not patient_id:
            cursor.execute("INSERT INTO patients (name) VALUES (?)", (patient_name,))
            conn.commit()
            patient_id = cursor.lastrowid

        query = """
        INSERT INTO predictions (
            patient_id, age, gender, ethnicity, education_level, poverty_income_ratio,
            bmi, weight_kg, height_cm, bp_systolic, bp_diastolic, blood_urea_nitrogen,
            albumin_serum, phosphorus, bicarbonate, calcium, uric_acid, urine_creatinine,
            urine_albumin, albumin_creatinine_ratio, diabetes_diagnosed, insulin_use,
            diabetes_pills, ever_smoked, current_smoker, predicted_stage, confidence,
            stage_probabilities
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """
        vals = (
            patient_id, input_data['age'], str(raw_input['gender']), str(raw_input['ethnicity']),
            input_data['education_level'], input_data['poverty_income_ratio'],
            input_data['bmi'], input_data['weight_kg'], input_data['height_cm'],
            input_data['bp_systolic'], input_data['bp_diastolic'], input_data['blood_urea_nitrogen'],
            input_data['albumin_serum'], input_data['phosphorus'], input_data['bicarbonate'],
            input_data['calcium'], input_data['uric_acid'], input_data['urine_creatinine'],
            input_data['urine_albumin'], input_data['albumin_creatinine_ratio'],
            input_data['diabetes_diagnosed'], input_data['insulin_use'], input_data['diabetes_pills'],
            input_data['ever_smoked'], input_data['current_smoker'],
            predicted_stage, confidence, json.dumps(probabilities)
        )
        cursor.execute(query, vals)
        conn.commit()
        prediction_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {"patient_id": patient_id, "prediction_id": prediction_id}
    except Exception as err:
        print(f"[WARNING] Failed to save prediction to SQLite: {err}")
        if conn:
            conn.close()
        return None

def load_artifacts():
    """Load model artifacts and encoders into memory on startup."""
    global rf_model, xgb_model, le_gender, le_ethnicity, le_target, meta
    print("Loading model artifacts from models/ directory...")
    rf_model = joblib.load(os.path.join(MODELS_DIR, "rf_model.pkl"))
    xgb_model = joblib.load(os.path.join(MODELS_DIR, "xgb_model.pkl"))
    le_gender = joblib.load(os.path.join(MODELS_DIR, "le_gender.pkl"))
    le_ethnicity = joblib.load(os.path.join(MODELS_DIR, "le_ethnicity.pkl"))
    le_target = joblib.load(os.path.join(MODELS_DIR, "le_target.pkl"))
    meta = joblib.load(os.path.join(MODELS_DIR, "pipeline_meta.pkl"))
    print("All models and preprocessing encoders loaded successfully!")

# Initialize Database and Load Artifacts
init_db()
load_artifacts()

# UI Routes
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/predict.html')
@app.route('/predict-page')
def serve_predict_page():
    return send_from_directory('.', 'predict.html')

@app.route('/results.html')
@app.route('/results-page')
def serve_results_page():
    return send_from_directory('.', 'results.html')

@app.route('/records.html')
@app.route('/records-page')
def serve_records_page():
    return send_from_directory('.', 'records.html')

@app.route('/patient.html')
@app.route('/patient-page')
def serve_patient_page():
    return send_from_directory('.', 'patient.html')



@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    conn = get_db_connection()
    db_status = "connected" if conn else "offline"
    if conn:
        conn.close()
    return jsonify({"status": "ok", "database": db_status}), 200

@app.route('/predict', methods=['POST'])
def predict():
    """
    Accepts JSON payload with 24 patient features, predicts CKD stage, and logs to SQLite DB.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request: Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Empty JSON payload received"}), 400

    if 'patient_name' not in data or not str(data['patient_name']).strip():
        return jsonify({"error": "Missing required field: patient_name"}), 400

    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        return jsonify({
            "error": "Missing required input fields",
            "missing_fields": missing_fields,
            "required_fields_count": len(REQUIRED_FIELDS),
            "received_fields_count": len(data)
        }), 400

    try:
        input_data = {}
        for field in REQUIRED_FIELDS:
            val = data[field]
            if val is None:
                val = meta['impute_values'].get(field, 0.0)
            input_data[field] = val

        gender_val = str(input_data['gender'])
        if gender_val in le_gender.classes_:
            input_data['gender'] = int(le_gender.transform([gender_val])[0])
        else:
            try:
                input_data['gender'] = int(float(gender_val))
            except ValueError:
                return jsonify({"error": f"Invalid gender value '{gender_val}'."}), 400

        ethnicity_val = str(input_data['ethnicity'])
        if ethnicity_val in le_ethnicity.classes_:
            input_data['ethnicity'] = int(le_ethnicity.transform([ethnicity_val])[0])
        else:
            try:
                input_data['ethnicity'] = int(float(ethnicity_val))
            except ValueError:
                return jsonify({"error": f"Invalid ethnicity value '{ethnicity_val}'."}), 400

        for col in meta['feature_names']:
            if col not in ['gender', 'ethnicity']:
                input_data[col] = float(input_data[col])

        input_df = pd.DataFrame([input_data])[meta['feature_names']]

        rf_probs = rf_model.predict_proba(input_df)
        xgb_probs = xgb_model.predict_proba(input_df)

        avg_probs = (rf_probs + xgb_probs) / 2.0
        pred_idx = int(np.argmax(avg_probs, axis=1)[0])

        predicted_stage = str(le_target.inverse_transform([pred_idx])[0])
        confidence = float(np.max(avg_probs))

        class_probabilities = {
            str(stage_name): round(float(prob), 4)
            for stage_name, prob in zip(le_target.classes_, avg_probs[0])
        }

        # Non-blocking SQLite persistence
        db_record = save_prediction_to_db(input_data, data, predicted_stage, round(confidence, 4), class_probabilities)

        res = {
            "patient_name": data['patient_name'],
            "predicted_stage": predicted_stage,
            "confidence": round(confidence, 4),
            "stage_probabilities": class_probabilities
        }
        if db_record:
            res["record_saved"] = True
            res["patient_id"] = db_record["patient_id"]
            res["prediction_id"] = db_record["prediction_id"]
        else:
            res["record_saved"] = False

        return jsonify(res), 200

    except Exception as e:
        return jsonify({"error": f"Internal prediction error: {str(e)}"}), 500

@app.route('/history', methods=['GET'])
def get_prediction_history():
    """Retrieves all past predictions (ordered by most recent first)."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database is offline / unavailable."}), 503

    try:
        cursor = conn.cursor()
        patient_id_filter = request.args.get('patient_id')
        limit = request.args.get('limit', default=50, type=int)

        if patient_id_filter:
            query = "SELECT p.*, pt.name as patient_name FROM predictions p JOIN patients pt ON p.patient_id = pt.id WHERE p.patient_id = ? ORDER BY p.created_at DESC LIMIT ?"
            cursor.execute(query, (patient_id_filter, limit))
        else:
            query = "SELECT p.*, pt.name as patient_name FROM predictions p JOIN patients pt ON p.patient_id = pt.id ORDER BY p.created_at DESC LIMIT ?"
            cursor.execute(query, (limit,))

        rows = [dict(row) for row in cursor.fetchall()]
        for row in rows:
            if isinstance(row.get('stage_probabilities'), str):
                row['stage_probabilities'] = json.loads(row['stage_probabilities'])
            if 'created_at' in row and row['created_at']:
                row['created_at'] = str(row['created_at'])

        cursor.close()
        conn.close()
        return jsonify({"count": len(rows), "history": rows}), 200
    except Exception as err:
        if conn:
            conn.close()
        return jsonify({"error": f"Failed to retrieve history: {str(err)}"}), 500

@app.route('/patient/<int:patient_id>', methods=['GET'])
def get_patient_monitoring_history(patient_id):
    """Retrieves patient details, longitudinal predictions (oldest to newest), and active alerts."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database is offline / unavailable."}), 503

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient_row = cursor.fetchone()

        if not patient_row:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Patient ID {patient_id} not found."}), 404
            
        patient = dict(patient_row)

        if 'created_at' in patient and patient['created_at']:
            patient['created_at'] = str(patient['created_at'])

        query = "SELECT * FROM predictions WHERE patient_id = ? ORDER BY created_at ASC, id ASC"
        cursor.execute(query, (patient_id,))
        predictions = [dict(row) for row in cursor.fetchall()]

        for row in predictions:
            if isinstance(row.get('stage_probabilities'), str):
                row['stage_probabilities'] = json.loads(row['stage_probabilities'])
            if 'created_at' in row and row['created_at']:
                row['created_at'] = str(row['created_at'])

        cursor.close()
        conn.close()

        alerts = evaluate_patient_alerts(predictions)

        return jsonify({
            "patient": patient,
            "prediction_count": len(predictions),
            "predictions": predictions,
            "alerts": alerts
        }), 200
    except Exception as err:
        if conn:
            conn.close()
        return jsonify({"error": f"Failed to retrieve patient monitoring record: {str(err)}"}), 500


@app.route('/prediction/<int:pred_id>', methods=['DELETE'])
def delete_prediction(pred_id):
    """Deletes a specific prediction record from SQLite database."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database is offline / unavailable."}), 503

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM predictions WHERE id = ?", (pred_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Prediction record ID {pred_id} not found."}), 404

        cursor.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": f"Prediction record ID {pred_id} deleted successfully."}), 200
    except Exception as err:
        if conn:
            conn.close()
        return jsonify({"error": f"Failed to delete prediction record: {str(err)}"}), 500

if __name__ == "__main__":
    print("Starting Flask Backend Server on http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
