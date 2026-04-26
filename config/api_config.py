"""
API configuration for the phishing URL detection system.
Defines Flask API server settings.
"""

import os

# ============================================================================
# API Configuration
# ============================================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 5000))
API_DEBUG = os.getenv("DEBUG", "false").lower() == "true"
API_WORKERS = int(os.getenv("API_WORKERS", 4))
