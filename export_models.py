import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

def train_and_export():
    print("Loading dataset for model export...")
    csv_path = r"C:\Users\HP\Desktop\Shalini\CKD Dataset 11k\CKD_NHANES_2021_2023.csv"
    df = pd.read_csv(csv_path)

    # Filter adults and drop unknown ckd_stage
    df = df[df['age'] >= 18].copy()
    df = df[df['ckd_stage'] != 'Unknown'].copy()

    categorical_cols = ['gender', 'ethnicity', 'diabetes_diagnosed', 'insulin_use', 'diabetes_pills', 'ever_smoked', 'current_smoker']
    exclude_cols = ['participant_id', 'egfr', 'serum_creatinine', 'ckd_present', 'ckd_stage']
    numeric_cols = [col for col in df.columns if col not in categorical_cols and col not in exclude_cols]

    # Calculate and store imputation values
    impute_values = {}
    for col in numeric_cols:
        val = float(df[col].median())
        impute_values[col] = val
        df[col] = df[col].fillna(val)

    for col in categorical_cols:
        if col in df.columns:
            mode_val = df[col].mode()[0]
            impute_values[col] = mode_val
            df[col] = df[col].fillna(mode_val)

    # Encoders
    le_gender = LabelEncoder()
    df['gender'] = le_gender.fit_transform(df['gender'].astype(str))

    le_ethnicity = LabelEncoder()
    df['ethnicity'] = le_ethnicity.fit_transform(df['ethnicity'].astype(str))

    le_target = LabelEncoder()
    y_encoded = le_target.fit_transform(df['ckd_stage'])

    # Prepare features
    drop_cols = ['participant_id', 'egfr', 'serum_creatinine', 'ckd_present', 'ckd_stage']
    X = df.drop(columns=drop_cols)
    feature_names = list(X.columns)

    # Stratified Train-Test Split (80/20)
    X_train, X_test, y_train_encoded, y_test_encoded = train_test_split(
        X, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
    )

    # SMOTE on training data
    print("Applying SMOTE oversampling to training data...")
    smote = SMOTE(random_state=42)
    X_train_smote, y_train_smote_encoded = smote.fit_resample(X_train, y_train_encoded)

    # Train Random Forest
    print("Training Random Forest model...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=6, class_weight='balanced', random_state=42)
    rf_model.fit(X_train_smote, y_train_smote_encoded)

    # Train XGBoost
    print("Training XGBoost model...")
    xgb_model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='mlogloss'
    )
    xgb_model.fit(X_train_smote, y_train_smote_encoded)

    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)

    # Save artifacts
    print("Saving models and artifacts to 'models/' directory...")
    joblib.dump(rf_model, os.path.join("models", "rf_model.pkl"))
    joblib.dump(xgb_model, os.path.join("models", "xgb_model.pkl"))
    joblib.dump(le_gender, os.path.join("models", "le_gender.pkl"))
    joblib.dump(le_ethnicity, os.path.join("models", "le_ethnicity.pkl"))
    joblib.dump(le_target, os.path.join("models", "le_target.pkl"))

    meta = {
        "feature_names": feature_names,
        "impute_values": impute_values,
        "categorical_cols": categorical_cols,
        "numeric_cols": numeric_cols
    }
    joblib.dump(meta, os.path.join("models", "pipeline_meta.pkl"))

    print("All models and preprocessing artifacts successfully exported to models/!")

if __name__ == "__main__":
    train_and_export()
