#!/usr/bin/env python3
"""
startup.py
==========
Production startup script for the Phishing URL Detection system.
Handles initialization, dataset download, model training, and API startup.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    AUTO_DOWNLOAD_DATASET,
    AUTO_TRAIN_MODELS,
)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)


BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║   PHISHING URL DETECTION - PRODUCTION STARTUP                        ║
║   UEL EUE | Level 4 Cybersecurity                                   ║
╚══════════════════════════════════════════════════════════════════════╝
"""


def main():
    """Main startup orchestration."""
    parser = argparse.ArgumentParser(description="Production startup orchestration")
    parser.add_argument(
        "--skip-dataset",
        action="store_true",
        help="Skip dataset download/validation"
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip model training"
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Start API without dataset/training"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="API port (default: 5000)"
    )
    args = parser.parse_args()

    print(BANNER)

    # Phase 1: Dataset
    if not args.skip_dataset and not args.api_only:
        logger.info("PHASE 1/3: Dataset Initialization")
        try:
            from dataset_manager import setup_dataset
            dataset_path = setup_dataset()
            logger.info(f"Dataset ready: {dataset_path}")
        except Exception as exc:
            logger.error(f"Dataset setup failed: {exc}")
            if not args.api_only:
                sys.exit(1)

    # Phase 2: Training
    if not args.skip_training and not args.api_only:
        logger.info("PHASE 2/3: Model Training")
        if AUTO_TRAIN_MODELS:
            try:
                from main import run_pipeline
                import argparse as ap
                pipeline_args = ap.Namespace(
                    data="data/raw/phishing_dataset.csv",
                    target="CLASS_LABEL",
                    eda_only=False,
                    skip_eda=True,
                )
                run_pipeline(pipeline_args)
                logger.info("Model training complete")
            except Exception as exc:
                logger.error(f"Model training failed: {exc}")
                sys.exit(1)
        else:
            logger.info("AUTO_TRAIN_MODELS=false, skipping training")
            logger.info("Use existing models or set AUTO_TRAIN_MODELS=true")

    # Phase 3: API Server
    logger.info("PHASE 3/3: Starting REST API")
    try:
        from app import app
        from config import API_HOST
        
        logger.info(f"API listening on {API_HOST}:{args.port}")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        
        # Show endpoint info
        print("\n" + "="*70)
        print("  AVAILABLE ENDPOINTS")
        print("="*70)
        print(f"  Health Check:  GET  http://localhost:{args.port}/health")
        print(f"  List Models:   GET  http://localhost:{args.port}/models")
        print(f"  Predict:       POST http://localhost:{args.port}/predict")
        print(f"  Batch Predict: POST http://localhost:{args.port}/predict-batch")
        print("="*70 + "\n")
        
        app.run(
            host=API_HOST,
            port=args.port,
            debug=False,
            use_reloader=False,
        )
    except Exception as exc:
        logger.error(f"API startup failed: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        sys.exit(0)
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        sys.exit(1)
