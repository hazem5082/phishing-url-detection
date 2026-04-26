"""
Logging configuration for the phishing URL detection system.
Defines logging format and levels.
"""

import os

# ============================================================================
# Logging Configuration
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if os.getenv("ENV", "production").lower() == "production" else "DEBUG")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s – %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
