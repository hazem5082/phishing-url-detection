# Phishing URL Detection – ML Project
**UEL EUE | Level 4 Cybersecurity | 48-Feature Kaggle Dataset**

**Status: ✅ Production-Ready**

---

## Quick Start (Production)

```bash
# 1. Clone and setup
git clone <repo>
cd phishing-url-detection

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure (optional - see .env.example)
cp .env.example .env

# 4. Download dataset & train models
python main.py

# 5. Start REST API
python app.py

# 6. Test the API
curl http://localhost:5000/health
```

---

## Docker Deployment (Recommended for Production)

```bash
# Build and run with Docker Compose
docker-compose up --build

# API will be available at: http://localhost:5000
```

### Docker Environment Variables

See `.env.example` for all configuration options. Key variables:

```bash
ENV=production              # Environment: production, development
AUTO_DOWNLOAD_DATASET=true  # Auto-download from Kaggle
AUTO_TRAIN_MODELS=false     # Set to true to retrain on startup
LOG_LEVEL=INFO              # Logging level: DEBUG, INFO, WARNING, ERROR
```

---

## API Endpoints

### Health Check
```bash
GET /health
# Returns: {"status": "ok", "models_loaded": 5, ...}
```

### List Available Models
```bash
GET /models
# Returns: {"models": ["XGBoost", "LogisticRegression", ...], "count": 5}
```

### Single Prediction
```bash
POST /predict
Content-Type: application/json

{
  "features": [0.5, 0.3, 0.1, ...],  # Array of 48 features
  "model": "XGBoost"                  # Optional model selection
}

# Response:
{
  "prediction": 1,
  "prediction_label": "Phishing",
  "confidence": 0.92,
  "model": "XGBoost",
  "timestamp": "2026-04-24T17:59:00"
}
```

### Batch Prediction
```bash
POST /predict-batch
Content-Type: application/json

{
  "features": [[0.5, ...], [0.3, ...]],
  "model": "XGBoost"
}

# Response: Array of predictions
```

---

## CLI Usage

### Main Pipeline
```bash
# Run full pipeline (auto-downloads dataset + trains models)
python main.py

# Run EDA only
python main.py --eda-only

# Skip EDA, train models only
python main.py --skip-eda

# Specify custom dataset location
python main.py --data data/raw/custom_phishing_dataset.csv

# Run tests
python -m pytest tests/ -v
```

### Offline URL Prediction
```bash
# Single URL prediction
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

### Production Startup
```bash
# Full startup (dataset + training + API)
python startup.py

# API only (skip dataset and training)
python startup.py --api-only

# Skip training only
python startup.py --skip-training

# Custom port
python startup.py --port 8080
```

### Environment Variables for CLI

```bash
# Auto-download dataset (default: true)
AUTO_DOWNLOAD_DATASET=false python main.py

# Skip EDA step
SKIP_EDA=true python main.py

# Change log level
LOG_LEVEL=DEBUG python main.py
```

---

## Dataset Management

### Auto-Download (Requires Kaggle API)

The project automatically downloads the Kaggle dataset on first run:

```bash
python main.py  # Automatically downloads if dataset missing
```

**Prerequisites:**
- Kaggle account (free)
- Kaggle API credentials (~/.kaggle/kaggle.json)
- Internet connection

See: https://www.kaggle.com/help/api

### Manual Download

If auto-download fails, download manually:

```bash
python dataset_manager.py
```

Or configure your Kaggle credentials:
```bash
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key
python dataset_manager.py
```

---

## Project Structure

```
project/
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── paths.py               # Directory and file paths
│   ├── model_config.py        # Model-related settings
│   ├── api_config.py          # API server settings
│   ├── logging_config.py      # Logging configuration
│   ├── runtime_config.py      # Runtime flags
│   └── environment.py         # Environment-specific settings
├── src/                        # Source code modules
│   ├── preprocessing/          # Data preprocessing
│   │   ├── data_loader.py     # Dataset loading and splitting
│   │   └── preprocessor.py    # Feature scaling and imputation
│   ├── feature_engineering/    # Feature extraction
│   │   └── feature_extractor.py  # URL to feature conversion
│   └── model_training/        # Model training pipeline
│       └── trainer.py         # Multi-model training with hyperparameter tuning
├── notebooks/                  # Jupyter notebooks
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_results_analysis.ipynb
├── tests/                      # Unit tests
│   ├── test_pipeline.py
│   └── test_api.py
├── doc/                        # Documentation
│   ├── architecture.md         # System architecture
│   ├── feature_engineering.md  # Feature documentation
│   └── user_guide.md          # User guide
├── errors/                     # Error logs and fixes
│   ├── error_log.md
│   └── README.md
├── data/                       # Data storage
│   ├── raw/                   # Raw dataset
│   └── processed/             # Processed splits
├── models_saved/               # Trained models (.pkl files)
├── reports/                    # Reports and visualizations
│   └── figures/               # EDA plots and confusion matrices
├── app.py                      # Flask REST API
├── main.py                     # Main pipeline entry point
├── predict_url.py              # Offline URL prediction CLI
├── dataset_manager.py          # Dataset download and management
├── eda.py                      # Standalone EDA script
├── startup.py                  # Production startup script
├── Dockerfile                  # Docker container
├── docker-compose.yml          # Docker orchestration
├── .env.example                # Environment template
└── requirements.txt
```

---

## EDA Figures Generated

| # | File | Description |
|---|------|-------------|
| 1 | `01_class_distribution_pie.png` | Donut chart of class balance |
| 2 | `02_class_distribution_bar.png` | Bar chart with counts + % |
| 3 | `03_correlation_heatmap.png` | Top-20 feature correlations |
| 4 | `04_feature_histograms.png` | UrlLength + NumDots distributions |
| 5 | `05_boxplots.png` | Phishing vs. Legitimate boxplots |
| 6 | `06_missing_value_matrix.png` | Missing data visualisation |
| 7 | `07_feature_importance.png` | ExtraTrees importance ranking |
| 8 | `08_pairplot_top_features.png` | Top-5 feature pairplot |

---

## Models & Hyperparameter Search

| Model | Key Tuned Params | CV Folds | N Iterations |
|-------|-----------------|----------|-------------|
| Logistic Regression | C, class_weight | 5 | 20 |
| Random Forest | n_estimators, max_depth, features | 5 | 20 |
| XGBoost | learning_rate, depth, subsample | 5 | 20 |
| Decision Tree | max_depth, criterion, leaf size | 5 | 20 |
| MLP Neural Net | hidden_layer_sizes, alpha, lr | 5 | 20 |

**Split: 70% train / 15% validation / 15% held-out test** (stratified)

---

## Expected Dataset Format

The Kaggle Phishing URL dataset should have:
- **48 numeric feature columns** (pre-extracted URL features)
- **1 label column** named `CLASS_LABEL` with values `{0, 1}`
  - `0` = Legitimate
  - `1` = Phishing

---

## Production Features

✅ **Auto-Dataset Download** - Downloads from Kaggle on first run  
✅ **REST API** - Serve predictions via HTTP endpoints  
✅ **Docker Ready** - One-command deployment  
✅ **Configuration Management** - Environment-based settings (split into modular config files)  
✅ **Health Checks** - Readiness and liveness probes  
✅ **Structured Logging** - Production-grade logging  
✅ **Batch Predictions** - Process multiple URLs at once  
✅ **Error Handling** - Comprehensive exception handling  
✅ **Model Serving** - Load and manage multiple trained models  
✅ **Testing** - Unit tests for core functionality  
✅ **Notebooks** - Jupyter notebooks for EDA, training, and analysis  
✅ **Documentation** - Comprehensive architecture, feature engineering, and user guide docs  
✅ **Error Tracking** - Centralized error log with documented fixes

---

## Contributing

See CONTRIBUTING.md for guidelines.

---

## License

MIT License - See LICENSE file for details.
