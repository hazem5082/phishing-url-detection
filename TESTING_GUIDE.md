# How to Test the Phishing URL Detection Project

## Overview

The project uses **48 pre-extracted numerical features** rather than raw URLs. This guide shows you how to test it in multiple ways.

---

## What Are the 48 Features?

The Kaggle dataset extracts features from URLs using techniques like:
- URL length analysis
- Domain structure analysis  
- Protocol validation
- Special character counting
- Path/query analysis
- TLD validation
- Domain validity checks

See `feature_extraction.py` for the complete feature extraction logic.

---

## Method 1: Automatic Feature Extraction (Easiest)

The `predict_url.py` script automatically extracts features from real URLs.

### Prerequisites
Make sure the API is running:
```bash
python startup.py
```

### Single URL Prediction

```bash
python predict_url.py "https://www.google.com"
```

Expected output:
```
Extracting features from URL: https://www.google.com

✓ URL: https://www.google.com
   Result:     Legitimate
   Confidence: 95.23%
   Model:      XGBoost
```

### Batch Prediction (Multiple URLs)

```bash
python predict_url.py "https://www.google.com" "https://www.github.com" "https://paypal-verify.tk"
```

Expected output:
```
================================================================================
BATCH PREDICTION RESULTS
================================================================================

[1/3] ✓ https://www.google.com
     -> Legitimate (confidence: 95.23%)

[2/3] ✓ https://www.github.com
     -> Legitimate (confidence: 92.15%)

[3/3] 🚨 https://paypal-verify.tk
     -> Phishing (confidence: 87.64%)

================================================================================
SUMMARY
================================================================================
Total URLs:     3
Phishing:       1 (33.3%)
Legitimate:     2 (66.7%)
================================================================================
```

### Interactive Mode

```bash
python predict_url.py --interactive
```

Then enter URLs one at a time:
```
Enter URL (or 'quit'): https://www.amazon.com
Extracting features from URL: https://www.amazon.com

✓ URL: https://www.amazon.com
   Result:     Legitimate
   Confidence: 94.12%
   Model:      XGBoost

Enter URL (or 'quit'): https://amaz0n-verify.tk
Extracting features from URL: https://amaz0n-verify.tk

🚨 URL: https://amaz0n-verify.tk
   Result:     Phishing
   Confidence: 89.45%
   Model:      XGBoost

Enter URL (or 'quit'): quit
Goodbye!
```

---

## Method 2: Direct API Testing (Using test_api.py)

### Setup

Make sure API is running:
```bash
python startup.py
```

### Run Full Test Suite

```bash
python test_api.py
```

This runs:
1. ✓ Health check
2. ✓ List available models
3. ✓ Single phishing prediction
4. ✓ Single legitimate prediction
5. ✓ Batch predictions
6. ✓ Model comparison
7. ✓ Error handling tests

### Example Output

```
TEST 1: Health Check
======================================================================
Status Code: 200
Response: {
  "status": "ok",
  "timestamp": "2026-04-24T18:15:30.123456",
  "models_loaded": 5,
  "available_models": [
    "XGBoost",
    "LogisticRegression",
    "RandomForest",
    "DecisionTree",
    "MLP"
  ]
}

TEST 2: List Available Models
======================================================================
Status Code: 200
Available Models: ['XGBoost', 'LogisticRegression', 'RandomForest', 'DecisionTree', 'MLP']
Count: 5

TEST 3: Single Prediction (XGBoost)
======================================================================
Status Code: 200
Response: {
  "prediction": 1,
  "prediction_label": "Phishing",
  "confidence": 0.92,
  "model": "XGBoost",
  "timestamp": "2026-04-24T18:15:31.234567"
}

...more tests...

TEST SUMMARY
======================================================================
Health Check                   PASS
List Models                    PASS
Phishing Prediction           PASS
Legitimate Prediction         PASS
Batch Predictions             PASS
Model Comparison              PASS

Total: 6/6 tests passed
======================================================================
```

---

## Method 3: Manual cURL Testing

### Health Check
```bash
curl http://localhost:5000/health
```

### List Models
```bash
curl http://localhost:5000/models
```

### Single Prediction with Raw Features

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      0.9, 0.8, -0.2, -0.1, -0.3, 0.4, 0.5, 0.6,
      -0.1, 0.5, -0.2, -0.3, 0.4, 0.7, -0.8, -0.9,
      -0.2, 0.3, -0.4, 0.2, -0.1, -0.2, 0.3, -0.4,
      0.5, -0.6, 0.3, -0.2, -0.1, 0.0, -0.1, -0.2,
      0.3, -0.4, 0.5, 0.1, -0.2, 0.3, -0.4, 0.5,
      -0.6, 0.7, -0.2, 0.3, -0.4, 0.5, -0.6, -0.7
    ],
    "model": "XGBoost"
  }'
```

### Batch Prediction with Raw Features

```bash
curl -X POST http://localhost:5000/predict-batch \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      [0.9, 0.8, ...48 features...],
      [-0.9, -0.8, ...48 features...]
    ],
    "model": "XGBoost"
  }'
```

---

## Method 4: Extract Features Then Use API

### Step 1: Extract features from a URL

```bash
python -c "
from feature_extraction import extract_features_from_url
features = extract_features_from_url('https://www.google.com')
print('Features:', features)
"
```

### Step 2: Use those features with the API

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [extracted_features_here],
    "model": "XGBoost"
  }'
```

---

## Method 5: Python Script Testing

### Direct API calls with requests

```python
import requests
from feature_extraction import extract_features_from_url

# Extract features from URL
url = "https://www.google.com"
features = extract_features_from_url(url)

# Send to API
response = requests.post(
    "http://localhost:5000/predict",
    json={"features": features, "model": "XGBoost"}
)

result = response.json()
print(f"URL: {url}")
print(f"Prediction: {result['prediction_label']}")
print(f"Confidence: {result['confidence']:.2%}")
```

---

## Testing Real-World URLs

### Legitimate URLs (Should predict 0 = Legitimate)
```bash
python predict_url.py \
  "https://www.google.com" \
  "https://www.github.com" \
  "https://www.wikipedia.org" \
  "https://www.amazon.com" \
  "https://www.facebook.com"
```

### Suspicious URLs (Should predict 1 = Phishing)
```bash
python predict_url.py \
  "http://paypal-verify.com/login.html" \
  "https://www.amaz0n.com/account" \
  "http://apple-signin.co.uk/verify" \
  "https://199.192.168.1/bank/login" \
  "http://secure-paypal.tk/verify"
```

---

## Testing Different Models

Each trained model has different accuracy characteristics:

### XGBoost (Recommended - Most Accurate)
```bash
python predict_url.py "https://www.google.com" --model XGBoost
```

### Logistic Regression (Fastest)
```bash
python predict_url.py "https://www.google.com" --model LogisticRegression
```

### Random Forest (Good Balance)
```bash
python predict_url.py "https://www.google.com" --model RandomForest
```

### Decision Tree (Interpretable)
```bash
python predict_url.py "https://www.google.com" --model DecisionTree
```

### MLP Neural Network (Experimental)
```bash
python predict_url.py "https://www.google.com" --model MLP
```

---

## Understanding Predictions

### Output Format
```json
{
  "prediction": 1,                    // 0 = Legitimate, 1 = Phishing
  "prediction_label": "Phishing",     // Human-readable label
  "confidence": 0.92,                 // Confidence score (0-1)
  "model": "XGBoost",                 // Which model made prediction
  "timestamp": "2026-04-24T18:15:30"  // When prediction was made
}
```

### Interpreting Confidence
- **0.90-1.00**: Very confident prediction
- **0.70-0.89**: Confident prediction
- **0.50-0.69**: Uncertain prediction
- **<0.50**: Very uncertain (typically flipped prediction)

### When Confidence is Low
Low confidence means the URL has mixed signals:
- Features typical of legitimate sites but some phishing indicators
- Features typical of phishing but some legitimate indicators
- New/unusual URL patterns

---

## Troubleshooting

### Error: "Could not connect to API"
**Solution**: Make sure API is running
```bash
python startup.py
```

### Error: "Expected 48 features, got X"
**Reason**: Feature array has wrong size
**Solution**: Use `extract_features_from_url()` to ensure 48 features

### Error: "Model 'XYZ' not found"
**Reason**: Model not available
**Solution**: Check available models with `python predict_url.py --models`

### Unexpected Low Accuracy
**Reasons**:
- Features not extracted correctly
- URL format unusual
- Model needs retraining with new data

---

## Batch Testing with Real Datasets

### Create a test URLs file (test_urls.txt)
```
https://www.google.com
https://www.github.com
http://suspicious-bank-login.tk
https://paypal-verify.com
https://www.wikipedia.org
```

### Process all URLs in Python
```python
with open('test_urls.txt') as f:
    urls = [line.strip() for line in f if line.strip()]

# Run predictions
import subprocess
cmd = ['python', 'predict_url.py'] + urls
subprocess.run(cmd)
```

---

## Performance Metrics

### Expected Performance
- **Single URL prediction**: ~10-50ms
- **Batch of 100 URLs**: ~500ms-2s
- **Model loading**: ~1-2 seconds on startup

### API Response Codes
- **200**: Successful prediction
- **400**: Invalid request (e.g., wrong feature count)
- **404**: Endpoint not found
- **500**: Server error (check logs)

---

## Advanced Testing

### Load Testing
```bash
# Test with 1000 URLs
python -c "
urls = ['https://www.example.com/page-' + str(i) for i in range(1000)]
import subprocess
subprocess.run(['python', 'predict_url.py'] + urls)
"
```

### Model Comparison on Same URLs
```bash
for model in XGBoost LogisticRegression RandomForest DecisionTree MLP; do
  echo "Testing with $model"
  python predict_url.py "https://www.google.com" --model $model
done
```

### Feature Analysis
```python
from feature_extraction import extract_features_from_url
import statistics

# Extract features from multiple URLs
urls = [
    "https://www.google.com",
    "https://www.github.com",
    "http://suspicious.tk"
]

for url in urls:
    features = extract_features_from_url(url)
    print(f"{url}:")
    print(f"  Mean: {statistics.mean(features):.3f}")
    print(f"  Stdev: {statistics.stdev(features):.3f}")
    print(f"  Min: {min(features):.3f}")
    print(f"  Max: {max(features):.3f}")
```

---

## Saving Test Results

### Save predictions to JSON
```bash
python predict_url.py "https://www.google.com" | python -m json.tool > results.json
```

### Batch export to CSV
```python
import csv
from feature_extraction import extract_features_from_url
import requests

urls = ["https://www.google.com", "https://github.com"]
results = []

for url in urls:
    features = extract_features_from_url(url)
    response = requests.post(
        "http://localhost:5000/predict",
        json={"features": features}
    )
    results.append({
        "url": url,
        "prediction": response.json()["prediction_label"],
        "confidence": response.json()["confidence"]
    })

with open('results.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=["url", "prediction", "confidence"])
    writer.writeheader()
    writer.writerows(results)
```

---

## Summary of Testing Methods

| Method | Ease | Speed | Best For |
|--------|------|-------|----------|
| `predict_url.py` | Very Easy | Fast | Testing individual URLs |
| `test_api.py` | Easy | Slow | Full test suite |
| cURL | Medium | Fast | CLI testing |
| Python + requests | Medium | Fast | Integration testing |
| Feature extraction | Hard | Varies | Understanding features |

---

## Next Steps

1. ✓ Start API: `python startup.py`
2. ✓ Test individual URL: `python predict_url.py "https://..."`
3. ✓ Run full test suite: `python test_api.py`
4. ✓ Customize feature extraction for your use case
5. ✓ Deploy to production with Docker

---

**Ready to test!** 🎯
