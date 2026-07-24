import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay

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
# We define categorical and numeric columns.
# Explicitly mentioned categorical columns: gender, ethnicity, diabetes_diagnosed, ever_smoked, current_smoker
# Let's also include other indicators like insulin_use, diabetes_pills.
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
# Target: ckd_stage
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

# =====================================================================
# Step 10: Train a Decision Tree Classifier (max_depth=5)
# =====================================================================
print("\nTraining Decision Tree Classifier (max_depth=5)...")
clf = DecisionTreeClassifier(max_depth=5, random_state=42)
clf.fit(X_train, y_train)

# =====================================================================
# Step 11: Evaluate on the test set
# =====================================================================
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n================ EVALUATION METRICS ================")
print(f"Accuracy: {accuracy:.4f}")

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred))

# Generate and save confusion matrix
print("Saving confusion matrix plot...")
cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)

fig, ax = plt.subplots(figsize=(10, 8))
disp.plot(cmap=plt.cm.Blues, ax=ax, xticks_rotation=45)
plt.title("Confusion Matrix for CKD Stage Prediction")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.close()
print("Confusion matrix saved as 'confusion_matrix.png'")

# =====================================================================
# Step 12: Save a visualization of the trained decision tree
# =====================================================================
print("Saving decision tree visualization...")
fig, ax = plt.subplots(figsize=(24, 12))
plot_tree(
    clf,
    feature_names=list(X.columns),
    class_names=list(clf.classes_),
    filled=True,
    rounded=True,
    fontsize=10,
    ax=ax
)
plt.title("Decision Tree Structure for CKD Stage Prediction", fontsize=16)
plt.tight_layout()
plt.savefig("decision_tree_structure.png", dpi=300)
plt.close()
print("Decision tree structure saved as 'decision_tree_structure.png'")

# =====================================================================
# Step 13: Print a table of 10 sample predictions vs actual stage
# =====================================================================
print("\n--- 10 Sample Predictions vs Actual Stages ---")
# Get indices of sample predictions
sample_indices = np.random.choice(len(y_test), 10, replace=False)
sample_actuals = y_test.iloc[sample_indices].values
sample_preds = y_pred[sample_indices]

# Print header
print(f"{'Index':<8} | {'Actual Stage':<15} | {'Predicted Stage':<15} | {'Match':<6}")
print("-" * 52)
for i in range(10):
    match = "Yes" if sample_actuals[i] == sample_preds[i] else "No"
    print(f"{sample_indices[i]:<8} | {sample_actuals[i]:<15} | {sample_preds[i]:<15} | {match:<6}")
print("-" * 52)
