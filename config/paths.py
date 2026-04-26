"""
Path configuration for the phishing URL detection system.
Defines all directory and file paths used throughout the project.
"""

import os
from pathlib import Path

# ============================================================================
# Environment & Base Paths
# ============================================================================
ENV = os.getenv("ENV", "production").lower()
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

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
