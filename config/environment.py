"""
Environment configuration for the phishing URL detection system.
Defines environment-specific settings (dev/prod/test).
"""

import os
from .paths import ENV


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
