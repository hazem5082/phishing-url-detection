import joblib
import pandas as pd
import numpy as np
import os
from src.preprocessing.preprocessor import PhishingPreprocessor

# 1. Choose Model
MODEL_NAME = "xgboost" # Options: xgboost, random_forest, mlp, etc.
MODEL_PATH = f"models_saved/{MODEL_NAME}.pkl"
DATA_PATH = "data/raw/Phishing_Legitimate_full.csv"

if not os.path.exists(MODEL_PATH):
    print(f"Error: Model not found at {MODEL_PATH}")
    exit(1)

print(f"--- Testing Model: {MODEL_NAME} ---")
model = joblib.load(MODEL_PATH)

# 2. Load data and pick a test sample
df = pd.read_csv(DATA_PATH)
target_col = "CLASS_LABEL"

# We pick 500 rows so the preprocessor has enough variance to work
sample_df = df.sample(500)
test_row = sample_df.iloc[[0]] # The specific row we will predict on

true_label = "PHISHING" if test_row[target_col].values[0] == 1 else "LEGITIMATE"
features_all = sample_df.drop(columns=[target_col, 'id'])
features_test = test_row.drop(columns=[target_col, 'id'])

# 3. Preprocess (Ensuring we always keep all 48 features)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(features_all.values)
X_scaled = scaler.transform(features_test.values)

# 4. Predict
prediction = model.predict(X_scaled)
probs = model.predict_proba(X_scaled)

pred_label = "PHISHING" if prediction[0] == 1 else "LEGITIMATE"
confidence = probs[0][prediction[0]] * 100

print(f"Real Status: {true_label}")
print(f"Prediction : {pred_label}")
print(f"Confidence : {confidence:.2f}%")

if true_label == pred_label:
    print("\n[OK] The model was CORRECT!")
else:
    print("\n[WRONG] The model was WRONG.")
