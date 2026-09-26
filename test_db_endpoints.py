import json
from app import app

def test_endpoints():
    client = app.test_client()

    print("--- 1. Testing GET /health ---")
    res_health = client.get('/health')
    print("Status:", res_health.status_code)
    print("Response:", res_health.get_json())
    assert res_health.status_code == 200

    print("\n--- 2. Testing POST /predict (Graceful DB Fallback) ---")
    payload = {
        "patient_name": "Test Patient",
        "age": 65.0,
        "gender": "Female",
        "ethnicity": "Non-Hispanic White",

        "education_level": 4.0,
        "poverty_income_ratio": 2.5,
        "bmi": 28.3,
        "weight_kg": 75.0,
        "height_cm": 162.0,
        "bp_systolic": 135.0,
        "bp_diastolic": 85.0,
        "blood_urea_nitrogen": 22.0,
        "albumin_serum": 4.1,
        "phosphorus": 3.8,
        "bicarbonate": 24.0,
        "calcium": 9.2,
        "uric_acid": 6.1,
        "urine_creatinine": 110.0,
        "urine_albumin": 25.0,
        "albumin_creatinine_ratio": 22.7,
        "diabetes_diagnosed": 1.0,
        "insulin_use": 2.0,
        "diabetes_pills": 1.0,
        "ever_smoked": 1.0,
        "current_smoker": 3.0
    }
    res_predict = client.post('/predict', json=payload)
    print("Status:", res_predict.status_code)
    print("Response:", json.dumps(res_predict.get_json(), indent=2))
    assert res_predict.status_code == 200
    assert "predicted_stage" in res_predict.get_json()
    assert "record_saved" in res_predict.get_json()

    print("\n--- 3. Testing GET /history ---")
    res_hist = client.get('/history')
    print("Status:", res_hist.status_code)
    print("Response:", res_hist.get_json())
    assert res_hist.status_code == 200

    print("\n--- 4. Testing GET /patient/1 (Single prediction -> no alerts) ---")
    res_pat1 = client.get('/patient/1')
    print("Status:", res_pat1.status_code)
    print("Response:", res_pat1.get_json())
    assert res_pat1.status_code == 200
    json_pat1 = res_pat1.get_json()
    assert "alerts" in json_pat1
    assert len(json_pat1["alerts"]) == 0  # 1 record -> no alerts

    print("\n--- 5. Testing POST /predict second visit for patient_id=1 with elevated BP & BUN ---")
    payload_visit2 = dict(payload)
    payload_visit2["patient_id"] = 1
    payload_visit2["patient_name"] = json_pat1["patient"]["name"]
    payload_visit2["bp_systolic"] = 160.0  # +25 mmHg increase (> 15)
    payload_visit2["blood_urea_nitrogen"] = 35.0  # +13 mg/dL increase (> 5)

    res_predict2 = client.post('/predict', json=payload_visit2)
    print("Status Visit 2:", res_predict2.status_code)
    assert res_predict2.status_code == 200

    print("\n--- 6. Testing GET /patient/1 (Longitudinal alerts verification) ---")
    res_pat2 = client.get('/patient/1')
    print("Status:", res_pat2.status_code)
    json_pat2 = res_pat2.get_json()
    print("Alerts generated:", json.dumps(json_pat2["alerts"], indent=2))
    assert res_pat2.status_code == 200
    assert json_pat2["prediction_count"] >= 2
    assert len(json_pat2["alerts"]) >= 1
    
    alert_types = [a["type"] for a in json_pat2["alerts"]]
    print("Alert types detected:", alert_types)
    assert "Blood Pressure Alert" in alert_types or "Lab Value Alert" in alert_types

    print("\n--- 7. Testing GET /patient/9999 (Invalid Patient ID -> 404) ---")
    res_invalid = client.get('/patient/9999')
    print("Status:", res_invalid.status_code)
    assert res_invalid.status_code == 404

    print("\nALL FLASK ENDPOINTS & HEALTH MONITORING ALERT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_endpoints()

