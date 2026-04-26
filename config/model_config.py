"""
Model configuration for the phishing URL detection system.
Defines model-related settings and hyperparameters.
"""

import os

# ============================================================================
# Model Configuration
# ============================================================================
TARGET_COLUMN = os.getenv("TARGET_COLUMN", "CLASS_LABEL")
TRAIN_TEST_SPLIT = 0.15  # 70/15/15 stratified split
VALIDATION_TEST_SPLIT = 0.5  # Of the 30% held-out, split into 15% val + 15% test

# ============================================================================
# Feature Configuration
# ============================================================================
N_FEATURES = 48  # Kaggle dataset has 48 numeric features
FEATURE_PREFIX = "Feature_"  # Prefix for generated feature names if needed
