import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

# =====================================================================
# Step 1: Load the CSV and print shape and column info
# =====================================================================
csv_path = r"C:\Users\HP\Desktop\Shalini\CKD Dataset 11k\CKD_NHANES_2021_2023.csv"
print("Loading dataset...")
df = pd.read_csv(csv_path)

print("\n--- Dataset Shape ---")
print(df.shape)

print("\n--- Column Dtypes and Non-Null Counts ---")
print(df.info())

# =====================================================================
# Step 2: Filter to adults only (age >= 18)
# =====================================================================
print("\nFiltering for adults (age >= 18)...")
df = df[df['age'] >= 18].copy()
print(f"Shape after age filtering: {df.shape}")

# =====================================================================
# Step 3: Drop rows where ckd_stage is "Unknown"
# =====================================================================
print("\nDropping rows where ckd_stage is 'Unknown'...")
df = df[df['ckd_stage'] != 'Unknown'].copy()
print(f"Shape after filtering out Unknown ckd_stage: {df.shape}")

# =====================================================================
# Step 4: Print the value counts of ckd_stage
# =====================================================================
print("\n--- CKD Stage Class Distribution ---")
stage_counts = df['ckd_stage'].value_counts()
print(stage_counts)

# =====================================================================
# Step 5: Handle missing values in feature columns
# =====================================================================
categorical_cols = ['gender', 'ethnicity', 'diabetes_diagnosed', 'insulin_use', 'diabetes_pills', 'ever_smoked', 'current_smoker']

# Exclude target and metadata from imputation
exclude_cols = ['participant_id', 'egfr', 'serum_creatinine', 'ckd_present', 'ckd_stage']

# Identify numeric columns for imputation
numeric_cols = [col for col in df.columns if col not in categorical_cols and col not in exclude_cols]

print("\nHandling missing values...")
# Impute numeric columns with median
for col in numeric_cols:
    if df[col].isnull().any():
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"Imputed numeric '{col}' with median: {median_val}")

# Impute categorical columns with mode
for col in categorical_cols:
    if col in df.columns and df[col].isnull().any():
        mode_val = df[col].mode()[0]
        df[col] = df[col].fillna(mode_val)
        print(f"Imputed categorical '{col}' with mode: {mode_val}")

# =====================================================================
# Step 6: Encode categorical columns using label encoding
# =====================================================================
print("\nEncoding categorical columns (gender, ethnicity)...")
le_gender = LabelEncoder()
df['gender'] = le_gender.fit_transform(df['gender'].astype(str))

le_ethnicity = LabelEncoder()
df['ethnicity'] = le_ethnicity.fit_transform(df['ethnicity'].astype(str))

print("Encoded gender classes:", dict(zip(le_gender.classes_, le_gender.transform(le_gender.classes_))))
print("Encoded ethnicity classes:", dict(zip(le_ethnicity.classes_, le_ethnicity.transform(le_ethnicity.classes_))))

# =====================================================================
# Steps 7 & 8: Set target and features
# =====================================================================
y = df['ckd_stage']

# Drop participant_id, egfr, serum_creatinine, ckd_present, and the target ckd_stage
drop_cols = ['participant_id', 'egfr', 'serum_creatinine', 'ckd_present', 'ckd_stage']
X = df.drop(columns=drop_cols)

print("\nFeatures used for training:")
print(list(X.columns))

# =====================================================================
# Step 9: Split into train/test sets (80/20), stratified by ckd_stage
# =====================================================================
print("\nSplitting dataset into train and test sets (80/20, stratified)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"Training set shape: {X_train.shape}")
print(f"Test set shape: {X_test.shape}")

# Dictionary to store performance metrics for summary table
model_results = {}
feature_importances = {}

# =====================================================================
# Step 10: Model 1 - Decision Tree Classifier (Original / Unbalanced)
# =====================================================================
print("\n================ MODEL 1: DECISION TREE (ORIGINAL / UNBALANCED) ================")
dt_orig = DecisionTreeClassifier(max_depth=5, random_state=42)
dt_orig.fit(X_train, y_train)

y_pred_dt_orig = dt_orig.predict(X_test)
acc_dt_orig = accuracy_score(y_test, y_pred_dt_orig)
rep_dt_orig = classification_report(y_test, y_pred_dt_orig, output_dict=True, zero_division=0)

print(f"Accuracy: {acc_dt_orig:.4f}")
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred_dt_orig, zero_division=0))

model_results["Decision Tree (Original)"] = {
    "Accuracy": acc_dt_orig,
    "Stage 4 F1": rep_dt_orig.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0),
    "Stage 5 F1": rep_dt_orig.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)
}

# Save original confusion matrix & DT structure plot
cm = confusion_matrix(y_test, y_pred_dt_orig, labels=dt_orig.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=dt_orig.classes_)
fig, ax = plt.subplots(figsize=(10, 8))
disp.plot(cmap=plt.cm.Blues, ax=ax, xticks_rotation=45)
plt.title("Confusion Matrix for CKD Stage Prediction (Decision Tree Original)")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.close()

fig, ax = plt.subplots(figsize=(24, 12))
plot_tree(
    dt_orig,
    feature_names=list(X.columns),
    class_names=list(dt_orig.classes_),
    filled=True,
    rounded=True,
    fontsize=10,
    ax=ax
)
plt.title("Decision Tree Structure for CKD Stage Prediction", fontsize=16)
plt.tight_layout()
plt.savefig("decision_tree_structure.png", dpi=300)
plt.close()

# =====================================================================
# Step 11: Model 2 - Decision Tree Classifier (Balanced Class Weights)
# =====================================================================
print("\n================ MODEL 2: DECISION TREE (BALANCED) ================")
dt_bal = DecisionTreeClassifier(max_depth=5, class_weight='balanced', random_state=42)
dt_bal.fit(X_train, y_train)

y_pred_dt_bal = dt_bal.predict(X_test)
acc_dt_bal = accuracy_score(y_test, y_pred_dt_bal)
rep_dt_bal = classification_report(y_test, y_pred_dt_bal, output_dict=True, zero_division=0)

print(f"Accuracy: {acc_dt_bal:.4f}")
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred_dt_bal, zero_division=0))

model_results["Decision Tree (Balanced)"] = {
    "Accuracy": acc_dt_bal,
    "Stage 4 F1": rep_dt_bal.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0),
    "Stage 5 F1": rep_dt_bal.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)
}
feature_importances["Decision Tree (Balanced)"] = dt_bal.feature_importances_

# =====================================================================
# Step 12: Model 3 - Random Forest Classifier
# =====================================================================
print("\n================ MODEL 3: RANDOM FOREST (BALANCED) ================")
rf_model = RandomForestClassifier(n_estimators=100, max_depth=6, class_weight='balanced', random_state=42)
rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)
acc_rf = accuracy_score(y_test, y_pred_rf)
rep_rf = classification_report(y_test, y_pred_rf, output_dict=True, zero_division=0)

print(f"Accuracy: {acc_rf:.4f}")
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred_rf, zero_division=0))

model_results["Random Forest"] = {
    "Accuracy": acc_rf,
    "Stage 4 F1": rep_rf.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0),
    "Stage 5 F1": rep_rf.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)
}
feature_importances["Random Forest"] = rf_model.feature_importances_

# =====================================================================
# Step 13: Model 4 - XGBoost Classifier (Encoded Target)
# =====================================================================
print("\n================ MODEL 4: XGBOOST ================")
# Encode target labels internally for XGBoost
le_target = LabelEncoder()
y_train_encoded = le_target.fit_transform(y_train)
y_test_encoded = le_target.transform(y_test)

# Compute sample weights to handle class imbalance in XGBoost
sample_weights = compute_sample_weight('balanced', y_train_encoded)

xgb_model = XGBClassifier(n_estimators=100, max_depth=6, random_state=42, eval_metric='mlogloss')
xgb_model.fit(X_train, y_train_encoded, sample_weight=sample_weights)

y_pred_xgb_encoded = xgb_model.predict(X_test)
y_pred_xgb = le_target.inverse_transform(y_pred_xgb_encoded)

acc_xgb = accuracy_score(y_test, y_pred_xgb)
rep_xgb = classification_report(y_test, y_pred_xgb, output_dict=True, zero_division=0)

print(f"Accuracy: {acc_xgb:.4f}")
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred_xgb, zero_division=0))

model_results["XGBoost"] = {
    "Accuracy": acc_xgb,
    "Stage 4 F1": rep_xgb.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0),
    "Stage 5 F1": rep_xgb.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)
}
feature_importances["XGBoost"] = xgb_model.feature_importances_

# =====================================================================
# Step 14: Side-by-Side Model Comparison Summary Table
# =====================================================================
print("\n" + "=" * 70)
print("                    MODEL COMPARISON SUMMARY TABLE")
print("=" * 70)
print(f"{'Model':<28} | {'Accuracy':<10} | {'Stage 4 F1':<12} | {'Stage 5 F1':<12}")
print("-" * 70)
for model_name, metrics in model_results.items():
    print(f"{model_name:<28} | {metrics['Accuracy']:<10.4f} | {metrics['Stage 4 F1']:<12.4f} | {metrics['Stage 5 F1']:<12.4f}")
print("=" * 70)

# =====================================================================
# Step 15: Feature Importance for Best Performing Model
# =====================================================================
# Determine best model based on accuracy (and Stage 4/5 F1 scores)
best_model_name = max(model_results.keys(), key=lambda m: (model_results[m]["Accuracy"], model_results[m]["Stage 4 F1"] + model_results[m]["Stage 5 F1"]))
print(f"\nBest Performing Model selected for Feature Importance: {best_model_name}")

if best_model_name in feature_importances:
    importances = feature_importances[best_model_name]
    feature_names = list(X.columns)
    
    # Sort features by importance score descending
    sorted_indices = np.argsort(importances)[::-1]
    
    print(f"\n--- Top 10 Most Important Features ({best_model_name}) ---")
    print(f"{'Rank':<6} | {'Feature Name':<30} | {'Importance Score':<15}")
    print("-" * 58)
    for rank in range(10):
        idx = sorted_indices[rank]
        print(f"{rank+1:<6} | {feature_names[idx]:<30} | {importances[idx]:<15.4f}")
    print("-" * 58)

# =====================================================================
# Step 16: Save Bar Chart Image (model_comparison.png)
# =====================================================================
print("\nSaving model accuracy comparison plot as 'model_comparison.png'...")
models = list(model_results.keys())
accuracies = [model_results[m]["Accuracy"] for m in models]

plt.figure(figsize=(10, 6))
bars = plt.bar(models, accuracies, color=['#3498db', '#e67e22', '#2ecc71', '#9b59b6'], edgecolor='black', alpha=0.85)

# Add values on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{height:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.ylim(0, 1.0)
plt.ylabel("Accuracy", fontsize=12)
plt.title("CKD Stage Prediction - Model Accuracy Comparison", fontsize=14, fontweight='bold')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("model_comparison.png", dpi=300)
plt.close()
print("Model comparison chart saved successfully.")

# =====================================================================
# Step 17: Sample Predictions (Decision Tree Original)
# =====================================================================
print("\n--- 10 Sample Predictions vs Actual Stages (Decision Tree Original) ---")
sample_indices = np.random.choice(len(y_test), 10, replace=False)
sample_actuals = y_test.iloc[sample_indices].values
sample_preds = y_pred_dt_orig[sample_indices]

print(f"{'Index':<8} | {'Actual Stage':<28} | {'Predicted Stage':<28} | {'Match':<6}")
print("-" * 75)
for i in range(10):
    match = "Yes" if sample_actuals[i] == sample_preds[i] else "No"
    print(f"{sample_indices[i]:<8} | {sample_actuals[i]:<28} | {sample_preds[i]:<28} | {match:<6}")
print("-" * 75)

# =====================================================================
# Step 18: SMOTE Oversampling & Tuned XGBoost Classifier
# =====================================================================
from imblearn.over_sampling import SMOTE

print("\n================ MODEL 5: TUNED XGBOOST WITH SMOTE ================")
print("\n--- Class Distribution in Training Set BEFORE SMOTE ---")
counts_before = pd.Series(le_target.inverse_transform(y_train_encoded)).value_counts()
print(counts_before)

# Apply SMOTE ONLY on the training data (never on the test data)
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote_encoded = smote.fit_resample(X_train, y_train_encoded)

print("\n--- Class Distribution in Training Set AFTER SMOTE ---")
counts_after = pd.Series(le_target.inverse_transform(y_train_smote_encoded)).value_counts()
print(counts_after)

# Train Tuned XGBoost on SMOTE-balanced training data
print("\nTraining Tuned XGBoost Classifier (n_estimators=200, max_depth=4, learning_rate=0.05)...")
xgb_tuned = XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    random_state=42,
    eval_metric='mlogloss'
)
xgb_tuned.fit(X_train_smote, y_train_smote_encoded)

# Evaluate on the original untouched test set
y_pred_xgb_tuned_encoded = xgb_tuned.predict(X_test)
y_pred_xgb_tuned = le_target.inverse_transform(y_pred_xgb_tuned_encoded)

acc_xgb_tuned = accuracy_score(y_test, y_pred_xgb_tuned)
rep_xgb_tuned = classification_report(y_test, y_pred_xgb_tuned, output_dict=True, zero_division=0)

print(f"\nAccuracy: {acc_xgb_tuned:.4f}")
print("\n--- Classification Report (Tuned XGBoost + SMOTE) ---")
print(classification_report(y_test, y_pred_xgb_tuned, zero_division=0))

stage4_f1_tuned = rep_xgb_tuned.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0)
stage5_f1_tuned = rep_xgb_tuned.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)

# =====================================================================
# Step 19: XGBoost Model Comparison Table (Original vs SMOTE + Tuned)
# =====================================================================
print("\n" + "=" * 75)
print("       XGBOOST COMPARISON: ORIGINAL (NO SMOTE) VS TUNED (WITH SMOTE)")
print("=" * 75)
print(f"{'XGBoost Version':<38} | {'Accuracy':<10} | {'Stage 4 F1':<12} | {'Stage 5 F1':<12}")
print("-" * 75)
print(f"{'Original XGBoost (No SMOTE)':<38} | {acc_xgb:<10.4f} | {model_results['XGBoost']['Stage 4 F1']:<12.4f} | {model_results['XGBoost']['Stage 5 F1']:<12.4f}")
print(f"{'New XGBoost (SMOTE + Tuned HP)':<38} | {acc_xgb_tuned:<10.4f} | {stage4_f1_tuned:<12.4f} | {stage5_f1_tuned:<12.4f}")
print("=" * 75)

# =====================================================================
# Step 20: XGBoost Hyperparameter Tuning with GridSearchCV
# =====================================================================
from sklearn.model_selection import GridSearchCV

print("\n================ MODEL 6: XGBOOST + SMOTE + GRIDSEARCHCV ================")
print("Starting GridSearchCV hyperparameter search (36 combinations, 5 folds)...")

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 4, 5, 6],
    'learning_rate': [0.01, 0.05, 0.1]
}

base_xgb = XGBClassifier(random_state=42, eval_metric='mlogloss')

grid_search = GridSearchCV(
    estimator=base_xgb,
    param_grid=param_grid,
    cv=5,
    scoring='f1_macro',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train_smote, y_train_smote_encoded)

print("\n--- GridSearchCV Results ---")
print(f"Best Hyperparameters: {grid_search.best_params_}")
print(f"Best Cross-Validation F1-Macro Score: {grid_search.best_score_:.4f}")

# Retrieve best model and evaluate on the untouched test set
best_xgb_model = grid_search.best_estimator_

y_pred_grid_encoded = best_xgb_model.predict(X_test)
y_pred_grid = le_target.inverse_transform(y_pred_grid_encoded)

acc_grid = accuracy_score(y_test, y_pred_grid)
rep_grid = classification_report(y_test, y_pred_grid, output_dict=True, zero_division=0)

print(f"\nAccuracy: {acc_grid:.4f}")
print("\n--- Classification Report (GridSearchCV Tuned XGBoost + SMOTE) ---")
print(classification_report(y_test, y_pred_grid, zero_division=0))

stage4_f1_grid = rep_grid.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0)
stage5_f1_grid = rep_grid.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)

# =====================================================================
# Step 21: Final Comprehensive XGBoost Comparison Table
# =====================================================================
print("\n" + "=" * 80)
print("             COMPREHENSIVE XGBOOST MODEL COMPARISON SUMMARY")
print("=" * 80)
print(f"{'XGBoost Model Variant':<42} | {'Accuracy':<10} | {'Stage 4 F1':<12} | {'Stage 5 F1':<12}")
print("-" * 80)
print(f"{'Original XGBoost (No SMOTE)':<42} | {acc_xgb:<10.4f} | {model_results['XGBoost']['Stage 4 F1']:<12.4f} | {model_results['XGBoost']['Stage 5 F1']:<12.4f}")
print(f"{'XGBoost + SMOTE (Manual Tuning)':<42} | {acc_xgb_tuned:<10.4f} | {stage4_f1_tuned:<12.4f} | {stage5_f1_tuned:<12.4f}")
print(f"{'XGBoost + SMOTE + GridSearchCV Tuning':<42} | {acc_grid:<10.4f} | {stage4_f1_grid:<12.4f} | {stage5_f1_grid:<12.4f}")
print("=" * 80)

# =====================================================================
# Step 22: BorderlineSMOTE + Best XGBoost Hyperparameters
# =====================================================================
from imblearn.over_sampling import BorderlineSMOTE, ADASYN

print("\n================ MODEL 7: BORDERLINESMOTE + XGBOOST (BEST HP) ================")
borderline_results = None

try:
    print("Applying BorderlineSMOTE to training data...")
    bsmote = BorderlineSMOTE(random_state=42)
    X_train_bsmote, y_train_bsmote_encoded = bsmote.fit_resample(X_train, y_train_encoded)
    
    xgb_bsmote = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='mlogloss'
    )
    xgb_bsmote.fit(X_train_bsmote, y_train_bsmote_encoded)
    
    y_pred_bsmote_encoded = xgb_bsmote.predict(X_test)
    y_pred_bsmote = le_target.inverse_transform(y_pred_bsmote_encoded)
    
    acc_bsmote = accuracy_score(y_test, y_pred_bsmote)
    rep_bsmote = classification_report(y_test, y_pred_bsmote, output_dict=True, zero_division=0)
    
    print(f"\nAccuracy: {acc_bsmote:.4f}")
    print("\n--- Classification Report (BorderlineSMOTE + Best HP XGBoost) ---")
    print(classification_report(y_test, y_pred_bsmote, zero_division=0))
    
    borderline_results = {
        "Accuracy": acc_bsmote,
        "Stage 4 F1": rep_bsmote.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0),
        "Stage 5 F1": rep_bsmote.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)
    }
except Exception as e:
    print(f"\n[WARNING] BorderlineSMOTE failed to execute: {e}")
    borderline_results = {"Accuracy": "Failed", "Stage 4 F1": "N/A", "Stage 5 F1": "N/A"}

# =====================================================================
# Step 23: ADASYN + Best XGBoost Hyperparameters
# =====================================================================
print("\n================ MODEL 8: ADASYN + XGBOOST (BEST HP) ================")
adasyn_results = None

try:
    print("Applying ADASYN to training data...")
    adasyn = ADASYN(random_state=42)
    X_train_adasyn, y_train_adasyn_encoded = adasyn.fit_resample(X_train, y_train_encoded)
    
    xgb_adasyn = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='mlogloss'
    )
    xgb_adasyn.fit(X_train_adasyn, y_train_adasyn_encoded)
    
    y_pred_adasyn_encoded = xgb_adasyn.predict(X_test)
    y_pred_adasyn = le_target.inverse_transform(y_pred_adasyn_encoded)
    
    acc_adasyn = accuracy_score(y_test, y_pred_adasyn)
    rep_adasyn = classification_report(y_test, y_pred_adasyn, output_dict=True, zero_division=0)
    
    print(f"\nAccuracy: {acc_adasyn:.4f}")
    print("\n--- Classification Report (ADASYN + Best HP XGBoost) ---")
    print(classification_report(y_test, y_pred_adasyn, zero_division=0))
    
    adasyn_results = {
        "Accuracy": acc_adasyn,
        "Stage 4 F1": rep_adasyn.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0),
        "Stage 5 F1": rep_adasyn.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)
    }
except Exception as e:
    print(f"\n[WARNING] ADASYN failed to execute: {e}")
    adasyn_results = {"Accuracy": "Failed", "Stage 4 F1": "N/A", "Stage 5 F1": "N/A"}

# =====================================================================
# Step 24: Comprehensive All-XGBoost Oversampling Comparison Table
# =====================================================================
print("\n" + "=" * 85)
print("             ALL XGBOOST OVERSAMPLING & TUNING VARIANTS COMPARISON")
print("=" * 85)
print(f"{'XGBoost Variant':<45} | {'Accuracy':<10} | {'Stage 4 F1':<12} | {'Stage 5 F1':<12}")
print("-" * 85)
print(f"{'Original XGBoost (No SMOTE)':<45} | {acc_xgb:<10.4f} | {model_results['XGBoost']['Stage 4 F1']:<12.4f} | {model_results['XGBoost']['Stage 5 F1']:<12.4f}")
print(f"{'XGBoost + SMOTE (Manual Tuning)':<45} | {acc_xgb_tuned:<10.4f} | {stage4_f1_tuned:<12.4f} | {stage5_f1_tuned:<12.4f}")
print(f"{'XGBoost + SMOTE + GridSearchCV Tuning':<45} | {acc_grid:<10.4f} | {stage4_f1_grid:<12.4f} | {stage5_f1_grid:<12.4f}")

if isinstance(borderline_results["Accuracy"], float):
    print(f"{'XGBoost + BorderlineSMOTE (Best HP)':<45} | {borderline_results['Accuracy']:<10.4f} | {borderline_results['Stage 4 F1']:<12.4f} | {borderline_results['Stage 5 F1']:<12.4f}")
else:
    print(f"{'XGBoost + BorderlineSMOTE (Best HP)':<45} | {'Failed':<10} | {'N/A':<12} | {'N/A':<12}")

if isinstance(adasyn_results["Accuracy"], float):
    print(f"{'XGBoost + ADASYN (Best HP)':<45} | {adasyn_results['Accuracy']:<10.4f} | {adasyn_results['Stage 4 F1']:<12.4f} | {adasyn_results['Stage 5 F1']:<12.4f}")
else:
    print(f"{'XGBoost + ADASYN (Best HP)':<45} | {'Failed':<10} | {'N/A':<12} | {'N/A':<12}")

print("=" * 85)

# =====================================================================
# Step 25: Stacked Ensemble Classifier (Random Forest + Best XGBoost)
# =====================================================================
print("\n================ MODEL 9: STACKED ENSEMBLE (RF + BEST XGBOOST) ================")
print("Training Random Forest on SMOTE-balanced training data...")
rf_smote = RandomForestClassifier(n_estimators=100, max_depth=6, class_weight='balanced', random_state=42)
rf_smote.fit(X_train_smote, y_train_smote_encoded)

print("Training Best XGBoost Model on SMOTE-balanced training data...")
best_xgb_ensemble = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric='mlogloss'
)
best_xgb_ensemble.fit(X_train_smote, y_train_smote_encoded)

# Predict class probabilities on test set
rf_probs = rf_smote.predict_proba(X_test)
xgb_probs = best_xgb_ensemble.predict_proba(X_test)

# Simple probability averaging ensemble
ensemble_probs = (rf_probs + xgb_probs) / 2.0
y_pred_ensemble_encoded = np.argmax(ensemble_probs, axis=1)
y_pred_ensemble = le_target.inverse_transform(y_pred_ensemble_encoded)

acc_ensemble = accuracy_score(y_test, y_pred_ensemble)
rep_ensemble = classification_report(y_test, y_pred_ensemble, output_dict=True, zero_division=0)

print(f"\nAccuracy: {acc_ensemble:.4f}")
print("\n--- Classification Report (Stacked Ensemble: RF + XGBoost) ---")
print(classification_report(y_test, y_pred_ensemble, zero_division=0))

stage4_f1_ensemble = rep_ensemble.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0)
stage5_f1_ensemble = rep_ensemble.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)

# Print confusion matrix array and save plot for Stacked Ensemble
cm_ensemble = confusion_matrix(y_test, y_pred_ensemble, labels=le_target.classes_)
print("\n--- Confusion Matrix (Stacked Ensemble Array) ---")
print(cm_ensemble)

print("\nSaving Stacked Ensemble confusion matrix plot as 'ensemble_confusion_matrix.png'...")
disp_ensemble = ConfusionMatrixDisplay(confusion_matrix=cm_ensemble, display_labels=le_target.classes_)
fig, ax = plt.subplots(figsize=(10, 8))
disp_ensemble.plot(cmap=plt.cm.Blues, ax=ax, xticks_rotation=45)
plt.title("Confusion Matrix for CKD Stage Prediction (Stacked Ensemble)")
plt.tight_layout()
plt.savefig("ensemble_confusion_matrix.png", dpi=300)
plt.close()
print("Stacked Ensemble confusion matrix saved as 'ensemble_confusion_matrix.png'")


# =====================================================================
# Step 26: Final All-Model Comparison Summary Table & Recommendation
# =====================================================================
print("\n" + "=" * 90)
print("              FINAL COMPREHENSIVE PIPELINE MODEL COMPARISON SUMMARY")
print("=" * 90)
print(f"{'Model / Ensemble Variant':<48} | {'Accuracy':<10} | {'Stage 4 F1':<12} | {'Stage 5 F1':<12}")
print("-" * 90)
print(f"{'Original XGBoost (No SMOTE)':<48} | {acc_xgb:<10.4f} | {model_results['XGBoost']['Stage 4 F1']:<12.4f} | {model_results['XGBoost']['Stage 5 F1']:<12.4f}")
print(f"{'XGBoost + SMOTE (Manual Tuning)':<48} | {acc_xgb_tuned:<10.4f} | {stage4_f1_tuned:<12.4f} | {stage5_f1_tuned:<12.4f}")
print(f"{'XGBoost + SMOTE + GridSearchCV Tuning':<48} | {acc_grid:<10.4f} | {stage4_f1_grid:<12.4f} | {stage5_f1_grid:<12.4f}")

if isinstance(borderline_results["Accuracy"], float):
    print(f"{'XGBoost + BorderlineSMOTE (Best HP)':<48} | {borderline_results['Accuracy']:<10.4f} | {borderline_results['Stage 4 F1']:<12.4f} | {borderline_results['Stage 5 F1']:<12.4f}")
else:
    print(f"{'XGBoost + BorderlineSMOTE (Best HP)':<48} | {'Failed':<10} | {'N/A':<12} | {'N/A':<12}")

if isinstance(adasyn_results["Accuracy"], float):
    print(f"{'XGBoost + ADASYN (Best HP)':<48} | {adasyn_results['Accuracy']:<10.4f} | {adasyn_results['Stage 4 F1']:<12.4f} | {adasyn_results['Stage 5 F1']:<12.4f}")
else:
    print(f"{'XGBoost + ADASYN (Best HP)':<48} | {'Failed':<10} | {'N/A':<12} | {'N/A':<12}")

print(f"{'Stacked Ensemble (RF + Best XGBoost)':<48} | {acc_ensemble:<10.4f} | {stage4_f1_ensemble:<12.4f} | {stage5_f1_ensemble:<12.4f}")
print("=" * 90)

# Check for model recommendation
print("\n--- RECOMMENDED FINAL MODEL CONCLUSION ---")
if acc_ensemble >= max(acc_xgb, acc_xgb_tuned, acc_grid) or (stage4_f1_ensemble + stage5_f1_ensemble) > (stage4_f1_grid + stage5_f1_grid):
    print("RECOMMENDED MODEL: Stacked Ensemble (Random Forest + XGBoost)")
    print(f"Reason: Achieves strong accuracy ({acc_ensemble:.4f}) with balanced Stage 4 ({stage4_f1_ensemble:.4f}) and Stage 5 ({stage5_f1_ensemble:.4f}) F1-scores by leveraging both tree-bagging and boosting ensemble diversity.")
else:
    print("RECOMMENDED MODEL: XGBoost + SMOTE + GridSearchCV Tuning")
    print(f"Reason: Achieves the highest overall accuracy ({acc_grid:.4f}) while preserving solid performance on rare stages (Stage 4 F1: {stage4_f1_grid:.4f}, Stage 5 F1: {stage5_f1_grid:.4f}).")

# =====================================================================
# Step 27: Feature Engineering & Retraining Stacked Ensemble
# =====================================================================
print("\n================ MODEL 10: STACKED ENSEMBLE WITH ENGINEERED FEATURES ================")
print("Creating 5 new engineered features...")

df_fe = df.copy()

# 1. Pulse Pressure
df_fe['pulse_pressure'] = df_fe['bp_systolic'] - df_fe['bp_diastolic']

# 2. Calcium-Phosphorus Product
df_fe['calcium_phosphorus_product'] = df_fe['calcium'] * df_fe['phosphorus']

# 3. BUN to Albumin Ratio
df_fe['bun_albumin_ratio'] = df_fe['blood_urea_nitrogen'] / (df_fe['albumin_serum'] + 0.01)

# 4. Age Group Categorization & Encoding
age_bins = [17, 30, 45, 60, 75, 120]
age_labels = ['18-30', '31-45', '46-60', '61-75', '75+']
df_fe['age_group'] = pd.cut(df_fe['age'], bins=age_bins, labels=age_labels)
le_age_group = LabelEncoder()
df_fe['age_group'] = le_age_group.fit_transform(df_fe['age_group'].astype(str))

# 5. BMI Category Binning & Encoding
bmi_bins = [0, 18.5, 25, 30, 100]
bmi_labels = ['Underweight', 'Normal', 'Overweight', 'Obese']
df_fe['bmi_category'] = pd.cut(df_fe['bmi'], bins=bmi_bins, labels=bmi_labels)
le_bmi = LabelEncoder()
df_fe['bmi_category'] = le_bmi.fit_transform(df_fe['bmi_category'].astype(str))

# Print first few rows of engineered features to verify correctness
new_feature_cols = ['pulse_pressure', 'calcium_phosphorus_product', 'bun_albumin_ratio', 'age_group', 'bmi_category']
print("\n--- First 5 Rows of New Engineered Features ---")
print(df_fe[new_feature_cols].head())

print("\nChecking for missing / infinite values in engineered features...")
print("NaN count:", df_fe[new_feature_cols].isnull().sum().to_dict())
print("Infinite count:", np.isinf(df_fe[new_feature_cols].select_dtypes(include=np.number)).sum().to_dict())

# Set features and target for engineered pipeline
y_fe = df_fe['ckd_stage']
X_fe = df_fe.drop(columns=drop_cols)

print(f"\nTotal features available after feature engineering: {X_fe.shape[1]}")

# Train/test split (80/20, stratified, same random_state=42)
X_train_fe, X_test_fe, y_train_fe, y_test_fe = train_test_split(
    X_fe, y_fe, test_size=0.20, random_state=42, stratify=y_fe
)

# Encode targets
y_train_fe_encoded = le_target.transform(y_train_fe)
y_test_fe_encoded = le_target.transform(y_test_fe)

# Apply SMOTE to the training set with engineered features
smote_fe = SMOTE(random_state=42)
X_train_fe_smote, y_train_fe_smote_encoded = smote_fe.fit_resample(X_train_fe, y_train_fe_encoded)

# Train RF & XGBoost models on SMOTE training set with engineered features
rf_fe = RandomForestClassifier(n_estimators=100, max_depth=6, class_weight='balanced', random_state=42)
rf_fe.fit(X_train_fe_smote, y_train_fe_smote_encoded)

xgb_fe = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric='mlogloss'
)
xgb_fe.fit(X_train_fe_smote, y_train_fe_smote_encoded)

# Predict class probabilities on test set
rf_probs_fe = rf_fe.predict_proba(X_test_fe)
xgb_probs_fe = xgb_fe.predict_proba(X_test_fe)

ensemble_probs_fe = (rf_probs_fe + xgb_probs_fe) / 2.0
y_pred_fe_encoded = np.argmax(ensemble_probs_fe, axis=1)
y_pred_fe = le_target.inverse_transform(y_pred_fe_encoded)

acc_fe = accuracy_score(y_test_fe, y_pred_fe)
rep_fe = classification_report(y_test_fe, y_pred_fe, output_dict=True, zero_division=0)

print(f"\nAccuracy (with Engineered Features): {acc_fe:.4f}")
print("\n--- Classification Report (Stacked Ensemble + Engineered Features) ---")
print(classification_report(y_test_fe, y_pred_fe, zero_division=0))

stage4_prec_fe = rep_fe.get("Stage 4 (Severely Decreased)", {}).get("precision", 0.0)
stage4_rec_fe = rep_fe.get("Stage 4 (Severely Decreased)", {}).get("recall", 0.0)
stage4_f1_fe = rep_fe.get("Stage 4 (Severely Decreased)", {}).get("f1-score", 0.0)

stage5_prec_fe = rep_fe.get("Stage 5 (Kidney Failure)", {}).get("precision", 0.0)
stage5_rec_fe = rep_fe.get("Stage 5 (Kidney Failure)", {}).get("recall", 0.0)
stage5_f1_fe = rep_fe.get("Stage 5 (Kidney Failure)", {}).get("f1-score", 0.0)

print("\n--- Detailed Metrics for Stage 4 & Stage 5 (Engineered Features) ---")
print(f"Stage 4 -> Precision: {stage4_prec_fe:.4f} | Recall: {stage4_rec_fe:.4f} | F1-Score: {stage4_f1_fe:.4f}")
print(f"Stage 5 -> Precision: {stage5_prec_fe:.4f} | Recall: {stage5_rec_fe:.4f} | F1-Score: {stage5_f1_fe:.4f}")

# =====================================================================
# Step 28: Before / After Feature Engineering Comparison Table
# =====================================================================
print("\n" + "=" * 80)
print("     BEFORE VS AFTER FEATURE ENGINEERING COMPARISON (STACKED ENSEMBLE)")
print("=" * 80)
print(f"{'Pipeline Variant':<42} | {'Accuracy':<10} | {'Stage 4 F1':<12} | {'Stage 5 F1':<12}")
print("-" * 80)
print(f"{'Stacked Ensemble (Original Features)':<42} | {acc_ensemble:<10.4f} | {stage4_f1_ensemble:<12.4f} | {stage5_f1_ensemble:<12.4f}")
print(f"{'Stacked Ensemble (Engineered Features)':<42} | {acc_fe:<10.4f} | {stage4_f1_fe:<12.4f} | {stage5_f1_fe:<12.4f}")
print("=" * 80)

print("\n--- FEATURE ENGINEERING CONCLUSION ---")
if acc_fe > acc_ensemble:
    print(f"RESULT: Feature Engineering IMPROVED overall accuracy from {acc_ensemble:.4f} to {acc_fe:.4f}.")
elif acc_fe == acc_ensemble:
    print(f"RESULT: Feature Engineering maintained the exact same accuracy ({acc_fe:.4f}).")
else:
    print(f"RESULT: Feature Engineering did not improve accuracy (changed from {acc_ensemble:.4f} to {acc_fe:.4f}).")






