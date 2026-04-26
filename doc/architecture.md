# Architecture Documentation

## Project Overview

This project implements a production-ready phishing URL detection system using machine learning. The system classifies URLs as either phishing or legitimate based on lexical and host-based features.

## System Architecture

```
phishing-url-detection/
├── config/                 # Configuration management
│   ├── __init__.py
│   ├── paths.py           # Directory and file paths
│   ├── model_config.py    # Model-related settings
│   ├── api_config.py      # API server settings
│   ├── logging_config.py  # Logging configuration
│   ├── runtime_config.py  # Runtime flags
│   └── environment.py     # Environment-specific settings
├── src/                   # Source code modules
│   ├── preprocessing/     # Data preprocessing
│   │   ├── data_loader.py    # Dataset loading and splitting
│   │   └── preprocessor.py   # Feature scaling and imputation
│   ├── feature_engineering/ # Feature extraction
│   │   └── feature_extractor.py  # URL to feature conversion
│   └── model_training/    # Model training pipeline
│       └── trainer.py     # Multi-model training with hyperparameter tuning
├── notebooks/             # Jupyter notebooks
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_results_analysis.ipynb
├── tests/                 # Unit tests
├── data/                  # Data storage
│   ├── raw/              # Raw dataset
│   └── processed/        # Processed splits
├── models_saved/          # Trained models (.pkl files)
├── reports/               # Reports and visualizations
│   └── figures/          # EDA plots and confusion matrices
├── doc/                   # Documentation
├── errors/                # Error logs and fixes
├── app.py                 # Flask REST API
├── main.py                # Main pipeline entry point
├── predict_url.py         # Offline URL prediction CLI
├── dataset_manager.py     # Dataset download and management
└── eda.py                 # Standalone EDA script
```

## Data Flow

### 1. Data Ingestion
- **Input**: Raw CSV dataset (Kaggle phishing dataset)
- **Location**: `data/raw/phishing_dataset.csv`
- **Format**: 48 numeric features + 1 label column (CLASS_LABEL)

### 2. Preprocessing Pipeline
```
Raw Data → Data Loader → Train/Val/Test Split (70/15/15) → Preprocessor
                                                    ↓
                                          - Imputation (median)
                                          - Constant feature removal
                                          - StandardScaler (fit on train only)
                                                    ↓
                                    Processed Feature Matrices
```

### 3. Model Training
```
Processed Data → Model Trainer → 5 Models with Hyperparameter Tuning
                                      ↓
                              - Logistic Regression
                              - Random Forest
                              - XGBoost
                              - Decision Tree
                              - MLP Neural Network
                                      ↓
                            Trained Models (.pkl files)
```

### 4. Prediction Pipeline
```
Raw URL → Feature Extractor (48 features) → Preprocessor → Model → Prediction
```

## Module Descriptions

### config/
Centralized configuration management using environment variables.

- **paths.py**: Defines all directory and file paths
- **model_config.py**: Model hyperparameters and feature settings
- **api_config.py**: Flask API server configuration
- **logging_config.py**: Logging format and levels
- **runtime_config.py**: Runtime flags (auto-download, auto-train, etc.)
- **environment.py**: Environment-specific settings (dev/prod/test)

### src/preprocessing/
Handles data loading, splitting, and preprocessing.

- **data_loader.py**:
  - Loads CSV dataset
  - Validates schema
  - Performs stratified 70/15/15 train/val/test split
  - Returns feature names

- **preprocessor.py**:
  - Median imputation for missing values
  - Removes constant (zero-variance) features
  - StandardScaler normalization (fit on train only)
  - Saves/loads preprocessor state
  - Label encoding validation

### src/feature_engineering/
Converts raw URLs to the 48 features expected by models.

- **feature_extractor.py**:
  - Extracts lexical features (length, dots, dashes, etc.)
  - Extracts host-based features (domain length, subdomain level, etc.)
  - Pads HTML-derived features with dataset medians
  - Returns 48-dimensional feature vector

### src/model_training/
Trains and evaluates multiple ML models.

- **trainer.py**:
  - Implements 5 ML algorithms
  - RandomizedSearchCV for hyperparameter tuning
  - 5-fold cross-validation
  - Generates classification reports and confusion matrices
  - Saves trained models as .pkl files

## Model Architecture

### 1. Logistic Regression
- **Type**: Linear classifier
- **Hyperparameters**: C, penalty, class_weight
- **Use Case**: Baseline model, interpretable

### 2. Random Forest
- **Type**: Ensemble of decision trees
- **Hyperparameters**: n_estimators, max_depth, min_samples_split, etc.
- **Use Case**: Robust ensemble, handles non-linear relationships

### 3. XGBoost
- **Type**: Gradient-boosted trees
- **Hyperparameters**: learning_rate, max_depth, subsample, etc.
- **Use Case**: State-of-the-art for tabular data

### 4. Decision Tree
- **Type**: Single decision tree
- **Hyperparameters**: max_depth, criterion, min_samples_leaf
- **Use Case**: Highly interpretable, explainability

### 5. MLP (Multi-Layer Perceptron)
- **Type**: Neural network
- **Hyperparameters**: hidden_layer_sizes, activation, alpha, learning_rate
- **Use Case**: Can learn complex non-linear feature interactions

## API Architecture

### Flask REST API (app.py)

**Endpoints**:
- `GET /health` - Health check and model status
- `GET /models` - List available models
- `POST /predict` - Single URL prediction
- `POST /predict-batch` - Batch prediction

**Request/Response Format**:
```json
// Request
{
  "features": [0.5, 0.3, 0.1, ...],  // 48 features
  "model": "XGBoost"                  // Optional
}

// Response
{
  "prediction": 1,
  "prediction_label": "Phishing",
  "confidence": 0.92,
  "model": "XGBoost",
  "timestamp": "2026-04-26T10:30:00"
}
```

## Deployment Architecture

### Docker Deployment
- **Dockerfile**: Multi-stage build for production
- **docker-compose.yml**: Orchestrates API service
- **Environment Variables**: Configured via .env file

### Production Features
- Auto-dataset download from Kaggle
- Health check endpoints
- Structured logging
- Error handling
- Model versioning
- Batch prediction support

## Security Considerations

1. **Data Privacy**: No sensitive data stored in models
2. **API Security**: Input validation, error handling
3. **Model Security**: Models saved as .pkl files, not exposed
4. **Environment Variables**: Sensitive config via .env

## Performance Optimization

1. **Model Caching**: Models loaded once at startup
2. **Batch Processing**: Support for multiple URL predictions
3. **Parallel Training**: n_jobs=-1 for sklearn models
4. **Feature Caching**: Preprocessor state saved for reuse

## Scalability

- **Horizontal Scaling**: Stateless API can be scaled via docker-compose
- **Model Serving**: Multiple models can be loaded simultaneously
- **Batch Processing**: Efficient handling of multiple predictions
- **Caching**: Preprocessor and models cached in memory

## Monitoring and Logging

- **Structured Logging**: JSON-formatted logs with timestamps
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Health Checks**: /health endpoint for monitoring
- **Metrics**: Accuracy, precision, recall, F1 score tracked
