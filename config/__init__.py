"""
Configuration module for phishing URL detection.
Loads settings from environment variables and config files.
"""

from .paths import DATA_RAW_DIR, DATA_PROCESSED_DIR, MODELS_DIR, REPORTS_DIR, DATASET_PATH, PROJECT_ROOT, KAGGLE_DATASET
from .model_config import TARGET_COLUMN, TRAIN_TEST_SPLIT, VALIDATION_TEST_SPLIT, N_FEATURES, FEATURE_PREFIX
from .api_config import API_HOST, API_PORT, API_DEBUG, API_WORKERS
from .logging_config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT
from .runtime_config import AUTO_DOWNLOAD_DATASET, AUTO_TRAIN_MODELS, SKIP_EDA
from .environment import ENV, get_config, ProductionConfig, DevelopmentConfig, TestingConfig

__all__ = [
    'ENV',
    'PROJECT_ROOT',
    'DATA_RAW_DIR',
    'DATA_PROCESSED_DIR',
    'MODELS_DIR',
    'REPORTS_DIR',
    'DATASET_PATH',
    'KAGGLE_DATASET',
    'TARGET_COLUMN',
    'TRAIN_TEST_SPLIT',
    'VALIDATION_TEST_SPLIT',
    'N_FEATURES',
    'FEATURE_PREFIX',
    'API_HOST',
    'API_PORT',
    'API_DEBUG',
    'API_WORKERS',
    'LOG_LEVEL',
    'LOG_FORMAT',
    'LOG_DATE_FORMAT',
    'AUTO_DOWNLOAD_DATASET',
    'AUTO_TRAIN_MODELS',
    'SKIP_EDA',
    'get_config',
    'ProductionConfig',
    'DevelopmentConfig',
    'TestingConfig',
]
