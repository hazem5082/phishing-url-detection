"""
Runtime configuration for the phishing URL detection system.
Defines runtime flags and behavior settings.
"""

import os

# ============================================================================
# Runtime Flags
# ============================================================================
AUTO_DOWNLOAD_DATASET = os.getenv("AUTO_DOWNLOAD_DATASET", "true").lower() == "true"
AUTO_TRAIN_MODELS = os.getenv("AUTO_TRAIN_MODELS", "true").lower() == "true"
SKIP_EDA = os.getenv("SKIP_EDA", "false").lower() == "true"
