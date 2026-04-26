"""
main.py
=======
Master entry-point that orchestrates the full Day-1 pipeline:

  Step 1 → Load raw dataset
  Step 2 → Preprocess (impute, scale, encode)
  Step 3 → Train / evaluate 5 models
  Step 4 → Save artefacts (models + figures)

Usage
-----
    python main.py --data data/raw/phishing_dataset.csv
    python main.py --data data/raw/phishing_dataset.csv --target Result
    python main.py --eda-only --data data/raw/phishing_dataset.csv
"""

import argparse
import logging
import sys
import time

from src.preprocessing.data_loader import load_dataset, split_data, get_feature_names
from src.preprocessing.preprocessor import PhishingPreprocessor, save_processed_splits
from src.model_training.trainer import run_all_models
from dataset_manager import DatasetManager
from config import AUTO_DOWNLOAD_DATASET, AUTO_TRAIN_MODELS

# ---------------------------------------------------------------------------
# Logging setup at INFO level for the full pipeline
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║      PHISHING URL DETECTION – Day 1 Pipeline                  ║
║      UEL EUE  |  Level 4 Cybersecurity Project               ║
║                                                               ║
║  Datasets:                                                    ║
║  [PRIMARY] Kaggle – shashwatwork (48 features, 'CLASS_LABEL' col)  ║
║  [REF]     HuggingFace – ealvaradob/phishing-dataset          ║
║  [REF]     PhishTank developer API                            ║
╚═══════════════════════════════════════════════════════════════╝
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Phishing URL Detection – full ML pipeline"
    )
    parser.add_argument(
        "--data",
        default="data/raw/Phishing_Legitimate_full.csv",
        help=(
            "Path to the raw Kaggle CSV dataset. "
            "Download: https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning"
        ),
    )
    parser.add_argument(
        "--target",
        default="CLASS_LABEL",
        help="Name of the label column (default: class — as used in the Shashwat Tiwari Kaggle dataset).",
    )
    parser.add_argument(
        "--eda-only",
        action="store_true",
        help="Run EDA visualisations only; skip model training.",
    )
    parser.add_argument(
        "--skip-eda",
        action="store_true",
        help="Skip EDA step; only run model training pipeline.",
    )
    return parser.parse_args()


def run_pipeline(args: argparse.Namespace) -> None:
    """
    Execute the end-to-end pipeline.

    Parameters
    ----------
    args : Parsed CLI arguments from argparse.
    """
    print(BANNER)
    t_start = time.perf_counter()

    # -----------------------------------------------------------------------
    # STEP 0 – Ensure dataset is available (auto-download if needed)
    # -----------------------------------------------------------------------
    logger.info("STEP 0/4 – Ensuring dataset availability …")
    try:
        dm = DatasetManager(auto_download=AUTO_DOWNLOAD_DATASET)
        dataset_path = dm.ensure_dataset()
        args.data = str(dataset_path)
        logger.info(f"Dataset ready: {dataset_path}")
    except Exception as exc:
        logger.error(f"Dataset unavailable: {exc}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # STEP 1 – Load dataset
    # -----------------------------------------------------------------------
    logger.info("STEP 1/4 – Loading dataset …")
    df = load_dataset(args.data)
    feature_names = get_feature_names(df, args.target)
    logger.info("Feature count: %d", len(feature_names))

    # -----------------------------------------------------------------------
    # STEP 2 – EDA (optional skip)
    # -----------------------------------------------------------------------
    if not args.skip_eda:
        logger.info("STEP 2/4 – Running EDA …")
        # Import here to avoid loading matplotlib at module level
        from eda import run_eda
        run_eda(args.data, args.target)
    else:
        logger.info("STEP 2/4 – EDA skipped (--skip-eda flag set).")

    if args.eda_only:
        logger.info("--eda-only flag set; stopping after EDA.")
        return

    # -----------------------------------------------------------------------
    # STEP 3 – Preprocessing
    # -----------------------------------------------------------------------
    logger.info("STEP 3/4 – Preprocessing …")

    # Split raw dataframe into 70/15/15
    X_train_raw, X_val_raw, X_test_raw, \
    y_train_raw, y_val_raw, y_test_raw = split_data(df, args.target)

    # Encode labels: -1 → 0  (XGBoost requires 0/1 integers)
    preprocessor = PhishingPreprocessor()
    y_train = preprocessor.encode_labels(y_train_raw)
    y_val   = preprocessor.encode_labels(y_val_raw)
    y_test  = preprocessor.encode_labels(y_test_raw)

    # Scale features (fit only on training data to prevent leakage)
    X_train = preprocessor.fit_transform(X_train_raw, feature_names)
    X_val   = preprocessor.transform(X_val_raw)
    X_test  = preprocessor.transform(X_test_raw)

    # Save preprocessor
    preprocessor.save("models_saved")

    # Persist clean CSVs for future notebook exploration
    save_processed_splits(
        (X_train, X_val, X_test, y_train, y_val, y_test),
        feature_names,
    )

    # -----------------------------------------------------------------------
    # STEP 4 – Model Training & Evaluation
    # -----------------------------------------------------------------------
    logger.info("STEP 4/4 – Training 5 models …")
    results = run_all_models(
        X_train, X_val, X_test,
        y_train, y_val, y_test,
    )

    # -----------------------------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------------------------
    elapsed = time.perf_counter() - t_start
    logger.info(
        "Pipeline complete in %.1f seconds. Best model by accuracy: %s",
        elapsed,
        max(results, key=lambda r: r["accuracy"])["name"],
    )
    print(f"\n✅  Day 1 pipeline finished in {elapsed:.1f}s")
    print("   Models saved → models_saved/")
    print("   Figures saved → reports/figures/")
    print("   Processed data → data/processed/\n")


if __name__ == "__main__":
    args = parse_args()
    try:
        run_pipeline(args)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Pipeline failed: %s", exc)
        sys.exit(1)
