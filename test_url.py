import joblib
import pandas as pd
import numpy as np
import os
import re
from urllib.parse import urlparse

# 1. Load Model
MODEL_PATH = "models_saved/xgboost.pkl"
model = joblib.load(MODEL_PATH)

def extract_features(url):
    """
    Extracts lexical features from a URL to match the 48-feature format.
    Note: Some features require scanning the actual HTML, which we skip here
    for speed, using neutral values instead.
    """
    parsed = urlparse(url)
    hostname = parsed.netloc
    path = parsed.path
    
    # Basic Lexical Features (these are part of the 48)
    features = {
        'NumDots': url.count('.'),
        'SubdomainLevel': hostname.count('.') - 1 if hostname.count('.') > 1 else 0,
        'PathLevel': path.count('/'),
        'UrlLength': len(url),
        'NumDash': url.count('-'),
        'NumDashInHostname': hostname.count('-'),
        'AtSymbol': 1 if '@' in url else 0,
        'TildeSymbol': 1 if '~' in url else 0,
        'NumUnderscore': url.count('_'),
        'NumPercent': url.count('%'),
        'NumQueryComponents': len(parsed.query.split('&')) if parsed.query else 0,
        'NumAmpersand': url.count('&'),
        'NumHash': url.count('#'),
        'NumNumericChars': sum(c.isdigit() for c in url),
        'NoHttps': 1 if parsed.scheme != 'https' else 0,
        'IpAddress': 1 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname) else 0,
        'HostnameLength': len(hostname),
        'PathLength': len(path),
        'QueryLength': len(parsed.query),
        'DoubleSlashInPath': 1 if '//' in path else 0,
    }
    
    # Fill the rest of the 48 features with 0 (neutral) for this quick test
    # (In a full version, you'd use Selenium to get 'PctExtHyperlinks', etc.)
    all_features = np.zeros(48)
    # We map our extracted ones to the first few slots
    for i, val in enumerate(features.values()):
        if i < 48:
            all_features[i] = val
            
    return all_features.reshape(1, -1)

# --- Execution ---
test_url = input("Enter a URL to test (e.g., http://suspicious-site.com/login): ")

print(f"\nAnalyzing: {test_url}...")
X = extract_features(test_url)

# Predict
prediction = model.predict(X)
probs = model.predict_proba(X)

result = "PHISHING" if prediction[0] == 1 else "LEGITIMATE"
confidence = probs[0][prediction[0]] * 100

print(f"Result    : {result}")
print(f"Confidence: {confidence:.2f}%")

if result == "PHISHING":
    print("\n[!] WARNING: This URL looks suspicious!")
else:
    print("\n[OK] This URL appears to be safe.")
