-- =====================================================================
-- CKD Stage Prediction System - Database Schema Script
-- Engine: SQLite
-- =====================================================================

-- Step 1: Create Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT DEFAULT 'Anonymous Patient',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Create Predictions History Table
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    
    -- 24 Clinical Input Features
    age REAL NOT NULL,
    gender TEXT NOT NULL,
    ethnicity TEXT NOT NULL,
    education_level REAL NOT NULL,
    poverty_income_ratio REAL NOT NULL,
    bmi REAL NOT NULL,
    weight_kg REAL NOT NULL,
    height_cm REAL NOT NULL,
    bp_systolic REAL NOT NULL,
    bp_diastolic REAL NOT NULL,
    blood_urea_nitrogen REAL NOT NULL,
    albumin_serum REAL NOT NULL,
    phosphorus REAL NOT NULL,
    bicarbonate REAL NOT NULL,
    calcium REAL NOT NULL,
    uric_acid REAL NOT NULL,
    urine_creatinine REAL NOT NULL,
    urine_albumin REAL NOT NULL,
    albumin_creatinine_ratio REAL NOT NULL,
    diabetes_diagnosed REAL NOT NULL,
    insulin_use REAL NOT NULL,
    diabetes_pills REAL NOT NULL,
    ever_smoked REAL NOT NULL,
    current_smoker REAL NOT NULL,

    -- Prediction Results & Metrics
    predicted_stage TEXT NOT NULL,
    confidence REAL NOT NULL,
    stage_probabilities TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key Constraint
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
