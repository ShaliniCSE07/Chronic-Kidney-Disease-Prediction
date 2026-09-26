import json
from app import app

def test_backend():
    client = app.test_client()

    print("--- 1. Testing GET /health ---")
    res_health = client.get('/health')
    print("Status Code:", res_health.status_code)
    print("Response:", res_health.get_json())
    assert res_health.status_code == 200
    assert res_health.get_json()["status"] == "ok"

    print("\n--- 2. Testing POST /predict with missing fields (Validation Test) ---")
    invalid_payload = {"patient_name": "Test Patient", "age": 60, "gender": "Female"}
    res_invalid = client.post('/predict', json=invalid_payload)
    print("Status Code:", res_invalid.status_code)
    print("Response:", res_invalid.get_json())
    assert res_invalid.status_code == 400
    assert "missing_fields" in res_invalid.get_json()

    print("\n--- 3. Testing POST /predict with full valid sample payload ---")
    valid_payload = {
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
    res_valid = client.post('/predict', json=valid_payload)
    print("Status Code:", res_valid.status_code)
    print("Response:", json.dumps(res_valid.get_json(), indent=2))
    assert res_valid.status_code == 200
    assert "predicted_stage" in res_valid.get_json()
    assert "confidence" in res_valid.get_json()

    print("\nALL BACKEND API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_backend()
