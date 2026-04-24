"""
config.py
=========
Production configuration management for the phishing URL detection system.
Supports environment-based settings (dev/prod) via .env file or environment variables.
"""

import os
from pathlib import Path

# ============================================================================
# Environment & Base Paths
# ============================================================================
ENV = os.getenv("ENV", "production").lower()
PROJECT_ROOT = Path(__file__).parent.absolute()

# ============================================================================
# Data Paths
# ============================================================================
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models_saved"
REPORTS_DIR = PROJECT_ROOT / "reports" / "figures"

# Ensure directories exist
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Expected dataset location
DATASET_PATH = DATA_RAW_DIR / "phishing_dataset.csv"

# Kaggle dataset identifier
KAGGLE_DATASET = "shashwatwork/phishing-dataset-for-machine-learning"

# ============================================================================
# Model Configuration
# ============================================================================
TARGET_COLUMN = os.getenv("TARGET_COLUMN", "CLASS_LABEL")
TRAIN_TEST_SPLIT = 0.15  # 70/15/15 stratified split
VALIDATION_TEST_SPLIT = 0.5  # Of the 30% held-out, split into 15% val + 15% test

# ============================================================================
# API Configuration
# ============================================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 5000))
API_DEBUG = os.getenv("DEBUG", "false").lower() == "true"
API_WORKERS = int(os.getenv("API_WORKERS", 4))

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENV == "production" else "DEBUG")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s – %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# Runtime Flags
# ============================================================================
AUTO_DOWNLOAD_DATASET = os.getenv("AUTO_DOWNLOAD_DATASET", "true").lower() == "true"
AUTO_TRAIN_MODELS = os.getenv("AUTO_TRAIN_MODELS", "true").lower() == "true"
SKIP_EDA = os.getenv("SKIP_EDA", "false").lower() == "true"

# ============================================================================
# Feature Configuration
# ============================================================================
N_FEATURES = 48  # Kaggle dataset has 48 numeric features
FEATURE_PREFIX = "Feature_"  # Prefix for generated feature names if needed


class ProductionConfig:
    """Production environment settings."""
    DEBUG = False
    TESTING = False
    ENV = "production"


class DevelopmentConfig:
    """Development environment settings."""
    DEBUG = True
    TESTING = False
    ENV = "development"


class TestingConfig:
    """Testing environment settings."""
    DEBUG = True
    TESTING = True
    ENV = "testing"


# Select config class based on environment
CONFIG = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}

CURRENT_CONFIG = CONFIG.get(ENV, ProductionConfig)


def get_config():
    """Get the current configuration object."""
    return CURRENT_CONFIG()


if __name__ == "__main__":
    # Print current configuration for debugging
    print(f"\n{'='*60}")
    print(f"  Phishing URL Detection - Configuration Report")
    print(f"{'='*60}")
    print(f"Environment:           {ENV}")
    print(f"Project Root:          {PROJECT_ROOT}")
    print(f"Data Raw Dir:          {DATA_RAW_DIR}")
    print(f"Data Processed Dir:    {DATA_PROCESSED_DIR}")
    print(f"Models Dir:            {MODELS_DIR}")
    print(f"Dataset Path:          {DATASET_PATH}")
    print(f"API Host:Port:         {API_HOST}:{API_PORT}")
    print(f"Auto Download:         {AUTO_DOWNLOAD_DATASET}")
    print(f"Auto Train Models:     {AUTO_TRAIN_MODELS}")
    print(f"Log Level:             {LOG_LEVEL}")
    print(f"{'='*60}\n")
