# Testing the Phishing URL Detection API - Quick Reference

## TL;DR - Quick Start

```bash
# 1. Start API in one terminal
python startup.py

# 2. Test with URLs in another terminal
python predict_url.py "https://www.google.com"
python predict_url.py "https://paypal-verify.tk"
python predict_url.py "https://www.amazon.com" "https://github.com" "https://suspicious.tk"
```

---

## Available Testing Tools

### 1. **predict_url.py** - Easiest (Recommended for Testing)

```bash
# Single URL
python predict_url.py "https://www.google.com"

# Multiple URLs
python predict_url.py "https://google.com" "https://github.com" "https://phishing-site.tk"

# Interactive mode
python predict_url.py --interactive

# With specific model
python predict_url.py "https://www.google.com" --model LogisticRegression
```

**Features:**
- Automatically extracts 48 features from URL
- Color-coded output (Red = Phishing, Green = Legitimate)
- Batch processing support
- Interactive mode for testing multiple URLs
- Works with real URLs directly

---

### 2. **test_api.py** - Comprehensive Test Suite

```bash
python test_api.py
```

**Runs:**
- Health check
- Model listing
- Single predictions (phishing & legitimate)
- Batch predictions
- Model comparison
- Error handling tests

---

### 3. **feature_extraction.py** - Feature Analysis

```bash
# Show example URLs and their extracted features
python feature_extraction.py

# Extract features programmatically
python -c "
from feature_extraction import extract_features_from_url
features = extract_features_from_url('https://google.com')
print(f'48 Features: {features}')
"
```

---

### 4. **Direct API Requests** - Manual Testing

```bash
# Health check
curl http://localhost:5000/health

# List models
curl http://localhost:5000/models

# Predict with raw features (48 required)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.5, 0.3, ...47 more...], "model": "XGBoost"}'
```

---

## Step-by-Step Testing Guide

### Step 1: Start the API
```bash
python startup.py

# Expected output:
# PHASE 1/3: Dataset Initialization
# PHASE 2/3: Model Training  
# PHASE 3/3: Starting REST API
# API listening on 0.0.0.0:5000
```

### Step 2: Test in Another Terminal

#### Option A: Quick Single URL Test
```bash
python predict_url.py "https://www.google.com"

# Expected:
# ✓ URL: https://www.google.com
#    Result:     Legitimate
#    Confidence: 95.23%
#    Model:      XGBoost
```

#### Option B: Test Multiple URLs
```bash
python predict_url.py \
  "https://www.google.com" \
  "https://www.github.com" \
  "https://paypal-verify.tk" \
  "https://suspicious-bank.co.uk"

# Shows summary with % phishing/legitimate
```

#### Option C: Run Full Test Suite
```bash
python test_api.py

# Tests all endpoints and shows PASS/FAIL summary
```

#### Option D: Interactive Mode
```bash
python predict_url.py --interactive

# Enter URLs one at a time:
# Enter URL (or 'quit'): https://www.example.com
# [Results displayed]
# Enter URL (or 'quit'): quit
```

---

## What's Being Tested

### The 48 Features Include:

1. **URL Structure** (Length, depth, complexity)
2. **Domain Analysis** (IP-based, subdomains, hyphens)
3. **Protocol** (HTTP vs HTTPS)
4. **Special Characters** (@, %, &, etc.)
5. **Path/Query Parameters**
6. **TLD Validation** (Common vs suspicious)
7. **Domain Validity** (Format, registration pattern)

### The Models Tested:

- **XGBoost** - Most accurate, recommended
- **Logistic Regression** - Fastest
- **Random Forest** - Good balance
- **Decision Tree** - Interpretable
- **MLP** - Neural network

---

## Sample Test Results

### Legitimate URL
```
URL: https://www.google.com
Result:     Legitimate
Confidence: 95.23%
```

### Phishing URL
```
URL: http://paypal-verify.com
Result:     Phishing
Confidence: 89.45%
```

### Suspicious/Uncertain
```
URL: https://199.168.1.1/bank
Result:     Phishing
Confidence: 72.15%  (Lower confidence = less certain)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Make sure API is running: `python startup.py` |
| "Expected 48 features" | Using raw feature array instead of URL - use `predict_url.py` |
| "Model not found" | Check spelling, use `python test_api.py` to list models |
| API starts but tests fail | Wait 10 seconds for model loading, then retry |
| Very slow predictions | First request loads models (~2-5s), subsequent are faster |

---

## Common Test Scenarios

### Scenario 1: Verify API is Working
```bash
python test_api.py
# Should show 6/6 tests PASSED
```

### Scenario 2: Test Your Own URLs
```bash
python predict_url.py \
  "https://your-site-1.com" \
  "https://your-site-2.com" \
  "https://your-site-3.com"
```

### Scenario 3: Compare Model Performance
```bash
# Run test_api.py - compares all 5 models on same data
python test_api.py
```

### Scenario 4: Batch Testing
```bash
# Create test_urls.txt with URLs (one per line)
echo "https://google.com" > test_urls.txt
echo "https://github.com" >> test_urls.txt
echo "https://suspicious.tk" >> test_urls.txt

# Test all URLs
python predict_url.py $(cat test_urls.txt)
```

### Scenario 5: Interactive Testing Session
```bash
python predict_url.py --interactive

# Test multiple URLs one by one
# Type 'models' to see available models
# Type 'quit' to exit
```

---

## Expected Performance

| Metric | Value |
|--------|-------|
| Single prediction | 10-50ms |
| 100 URLs batch | 500ms - 2s |
| Model loading | 1-2 seconds |
| API startup | 3-10 seconds |

---

## Key Files for Testing

| File | Purpose |
|------|---------|
| `predict_url.py` | **USE THIS** - Test with real URLs |
| `test_api.py` | Full API test suite |
| `feature_extraction.py` | Feature analysis & extraction |
| `TESTING_GUIDE.md` | Detailed testing documentation |
| `app.py` | API server |
| `startup.py` | Start API + dataset/models |

---

## Testing Checklist

- [ ] API running: `python startup.py`
- [ ] Single URL works: `python predict_url.py "https://google.com"`
- [ ] Multiple URLs work: `python predict_url.py "url1" "url2" "url3"`
- [ ] Interactive mode works: `python predict_url.py --interactive`
- [ ] Full test suite passes: `python test_api.py`
- [ ] Different models tested with `--model` flag
- [ ] Batch predictions under 2 seconds for 100 URLs
- [ ] API returns confidence scores
- [ ] Health check responds: `curl http://localhost:5000/health`

---

## Next Steps

1. **Quick Test**: `python predict_url.py "https://www.example.com"`
2. **Full Validation**: `python test_api.py`
3. **Integration**: Use API in your application
4. **Deployment**: Deploy with Docker: `docker-compose up`

---

**Questions?** See `TESTING_GUIDE.md` for detailed documentation.
