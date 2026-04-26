# User Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Dataset Setup](#dataset-setup)
4. [Training Models](#training-models)
5. [Making Predictions](#making-predictions)
6. [API Usage](#api-usage)
7. [Notebooks](#notebooks)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional, for cloning)

### Step 1: Clone or Download
```bash
git clone <repository-url>
cd phishing-url-detection
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment (Optional)
```bash
cp .env.example .env
# Edit .env with your settings
```

## Quick Start

### Option 1: Full Pipeline (Recommended)
```bash
python main.py
```
This will:
1. Download the dataset (if not present)
2. Run EDA visualizations
3. Preprocess the data
4. Train all 5 models
5. Save models and reports

### Option 2: EDA Only
```bash
python main.py --eda-only
```

### Option 3: Skip EDA
```bash
python main.py --skip-eda
```

## Dataset Setup

### Automatic Download
The system automatically downloads the Kaggle dataset on first run if:
- `AUTO_DOWNLOAD_DATASET=true` (default)
- Kaggle API credentials are configured

### Manual Download
If auto-download fails, download manually:

1. Go to: https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning
2. Download the dataset
3. Save as: `data/raw/phishing_dataset.csv`

### Kaggle API Setup
```bash
# Install Kaggle API
pip install kaggle

# Configure credentials
# 1. Go to https://www.kaggle.com/account
# 2. Create API token
# 3. Save kaggle.json to ~/.kaggle/ (Linux/Mac) or %USERPROFILE%\.kaggle\ (Windows)
```

## Training Models

### Using Command Line
```bash
# Full pipeline
python main.py

# Custom dataset location
python main.py --data /path/to/dataset.csv

# Custom target column
python main.py --target CLASS_LABEL
```

### Using Jupyter Notebook
```bash
jupyter notebook notebooks/02_model_training.ipynb
```

### Model Output
Trained models are saved to `models_saved/`:
- `logistic_regression.pkl`
- `random_forest.pkl`
- `xgboost.pkl`
- `decision_tree.pkl`
- `mlp.pkl`
- `preprocessor.pkl`

## Making Predictions

### Option 1: Command Line (Offline)
```bash
# Single URL
python predict_url.py "https://www.example.com"

# Multiple URLs
python predict_url.py "https://example.com" "https://google.com"

# Interactive mode
python predict_url.py --interactive

# List available models
python predict_url.py --list-models

# Use specific model
python predict_url.py --model random_forest "https://example.com"
```

### Option 2: REST API
```bash
# Start API server
python app.py

# Make prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.5, 0.3, 0.1, ...], "model": "XGBoost"}'
```

### Option 3: Python Script
```python
from src.feature_engineering.feature_extractor import extract_features_from_url
from src.preprocessing.preprocessor import PhishingPreprocessor
import joblib
import numpy as np

# Load model and preprocessor
model = joblib.load('models_saved/xgboost.pkl')
preprocessor = PhishingPreprocessor.load('models_saved/preprocessor.pkl')

# Extract features
url = "https://www.example.com"
features = extract_features_from_url(url)
features_array = np.array(features).reshape(1, -1)

# Preprocess
features_scaled = preprocessor.transform(features_array)

# Predict
prediction = model.predict(features_scaled)[0]
probability = model.predict_proba(features_scaled)[0, 1]

print(f"Prediction: {'Phishing' if prediction == 1 else 'Legitimate'}")
print(f"Confidence: {probability:.2%}")
```

## API Usage

### Start the Server
```bash
python app.py
```
Server runs on `http://localhost:5000` by default.

### Endpoints

#### Health Check
```bash
GET /health
```
Response:
```json
{
  "status": "ok",
  "timestamp": "2026-04-26T10:30:00",
  "models_loaded": 5,
  "available_models": ["logistic_regression", "random_forest", "xgboost", "decision_tree", "mlp"]
}
```

#### List Models
```bash
GET /models
```
Response:
```json
{
  "models": ["logistic_regression", "random_forest", "xgboost", "decision_tree", "mlp"],
  "count": 5,
  "timestamp": "2026-04-26T10:30:00"
}
```

#### Single Prediction
```bash
POST /predict
Content-Type: application/json

{
  "features": [0.5, 0.3, 0.1, ...],  // 48 features
  "model": "XGBoost"                  // Optional
}
```
Response:
```json
{
  "prediction": 1,
  "prediction_label": "Phishing",
  "confidence": 0.92,
  "model": "XGBoost",
  "timestamp": "2026-04-26T10:30:00"
}
```

#### Batch Prediction
```bash
POST /predict-batch
Content-Type: application/json

{
  "features": [[0.5, ...], [0.3, ...]],  // Array of feature arrays
  "model": "XGBoost"
}
```
Response:
```json
{
  "predictions": [
    {"id": 0, "prediction": 1, "prediction_label": "Phishing", "confidence": 0.92},
    {"id": 1, "prediction": 0, "prediction_label": "Legitimate", "confidence": 0.88}
  ],
  "count": 2,
  "model": "XGBoost",
  "timestamp": "2026-04-26T10:30:00"
}
```

## Notebooks

### 01_exploratory_data_analysis.ipynb
Performs EDA on the dataset:
- Class distribution analysis
- Correlation heatmap
- Feature distributions
- Missing value analysis
- Feature importance ranking

Run:
```bash
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb
```

### 02_model_training.ipynb
Trains and evaluates models:
- Data loading and preprocessing
- Model training with hyperparameter tuning
- Performance comparison

Run:
```bash
jupyter notebook notebooks/02_model_training.ipynb
```

### 03_results_analysis.ipynb
Analyzes model results:
- Performance metrics comparison
- ROC curves
- Feature importance analysis
- Best model detailed analysis

Run:
```bash
jupyter notebook notebooks/03_results_analysis.ipynb
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Environment
ENV=production

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=false
API_WORKERS=4

# Runtime Flags
AUTO_DOWNLOAD_DATASET=true
AUTO_TRAIN_MODELS=true
SKIP_EDA=false

# Logging
LOG_LEVEL=INFO

# Model Configuration
TARGET_COLUMN=CLASS_LABEL
```

### Config Files
Configuration is split into multiple files in the `config/` directory:
- `paths.py`: Directory and file paths
- `model_config.py`: Model settings
- `api_config.py`: API settings
- `logging_config.py`: Logging settings
- `runtime_config.py`: Runtime flags
- `environment.py`: Environment-specific settings

## Troubleshooting

### Dataset Not Found
**Error**: `FileNotFoundError: Dataset not found`

**Solution**:
```bash
# Enable auto-download
export AUTO_DOWNLOAD_DATASET=true
python main.py

# Or download manually
python dataset_manager.py
```

### Kaggle API Error
**Error**: `Kaggle API credentials not found`

**Solution**:
1. Go to https://www.kaggle.com/account
2. Create API token
3. Save `kaggle.json` to `~/.kaggle/` (Linux/Mac) or `%USERPROFILE%\.kaggle\` (Windows)

### Model Not Found
**Error**: `Model 'xgboost' not found`

**Solution**:
```bash
# Train models first
python main.py --skip-eda
```

### Import Error
**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure you're in the project root
cd phishing-url-detection

# Install dependencies
pip install -r requirements.txt
```

### Port Already in Use
**Error**: `Address already in use`

**Solution**:
```bash
# Change port
export API_PORT=5001
python app.py

# Or kill the process using the port
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Memory Error
**Error**: `MemoryError` during training

**Solution**:
- Use smaller hyperparameter ranges in `src/model_training/trainer.py`
- Reduce `n_estimators` for tree-based models
- Use a smaller dataset subset for testing

## Performance Tips

1. **Use GPU**: XGBoost can use GPU for faster training
2. **Parallel Training**: Models already use `n_jobs=-1` for parallel processing
3. **Batch Predictions**: Use batch endpoint for multiple URLs
4. **Model Caching**: Models are cached in memory after first load
5. **Preprocessor Reuse**: Preprocessor is saved and reused for predictions

## Best Practices

1. **Always use virtual environments** to avoid dependency conflicts
2. **Keep .env file secure** and don't commit it to version control
3. **Use the appropriate model** for your use case (XGBoost for accuracy, Decision Tree for interpretability)
4. **Monitor model performance** regularly and retrain if needed
5. **Validate URLs** before feature extraction to handle edge cases
6. **Use batch predictions** for processing multiple URLs efficiently
