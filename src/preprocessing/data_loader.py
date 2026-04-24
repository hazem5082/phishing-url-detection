"""
src/preprocessing/data_loader.py
=================================
Handles loading the Kaggle Phishing URL dataset (48 pre-extracted features),
validates schema integrity, and produces the 70 / 15 / 15 train/val/test splits.

Dataset source
--------------
  Primary : Kaggle – "Phishing Dataset for Machine Learning" by Shashwat Tiwari
            https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning
            5,000 phishing + 5,000 legitimate webpages; 48 Selenium-extracted features.
            Label column : 'CLASS_LABEL'  →  1 = Phishing,  0 = Legitimate

  Reference : HuggingFace – ealvaradob/phishing-dataset (text/URL pairs, text='text', label)
              https://huggingface.co/datasets/ealvaradob/phishing-dataset
              (NLP-oriented; used for context / future BERT extension, not this pipeline)

  Reference : PhishTank developer download
              https://www.phishtank.com/developer_info.php
              (CSV of verified-live phishing URLs; phishing-only, no negatives)
              Fields: phish_id, url, phish_detail_url, submission_time,
                      verified, verification_time, online, target

Split strategy
--------------
  70 % → training
  15 % → validation  (used during hyperparameter search)
  15 % → held-out test (reported in final metrics)
"""

import os
import logging
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RANDOM_SEED = 42                          # Reproducibility seed
TARGET_COLUMN = "CLASS_LABEL"                   # Label column in the Kaggle dataset
TRAIN_RATIO = 0.70                        # 70 % training
VAL_RATIO   = 0.15                        # 15 % validation
TEST_RATIO  = 0.15                        # 15 % test


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Load the Kaggle phishing dataset from a CSV file.

    Expected dataset
    ----------------
    Kaggle: shashwatwork/phishing-dataset-for-machine-learning
    - 10,000 rows  (5,000 phishing + 5,000 legitimate)
    - 48 numeric feature columns extracted with Selenium WebDriver
    - 1 label column named 'CLASS_LABEL':  1 = Phishing,  0 = Legitimate
    - No -1 values; labels are already binary {0, 1}

    Parameters
    ----------
    filepath : str
        Absolute or relative path to the raw CSV file.
        Download from: https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning
        Save as: data/raw/Phishing_Legitimate_full.csv

    Returns
    -------
    pd.DataFrame
        Raw DataFrame with all 48 features + 'CLASS_LABEL' label column.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If the expected target column is absent from the file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at '{filepath}'.\n"
            "Download from: https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning\n"
            "Expected filename: Phishing_Legitimate_full.csv  →  save to data/raw/"
        )

    logger.info("Loading dataset from: %s", filepath)
    df = pd.read_csv(filepath)
    
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # Basic schema validation – check the correct label column name
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' not found in the file.\n"
            f"Available columns: {list(df.columns)}\n"
            "Make sure you downloaded the Shashwat Tiwari Kaggle dataset "
            "(shashwatwork/phishing-dataset-for-machine-learning)."
        )

    logger.info(
        "Dataset loaded. Shape: %s  |  Label distribution:\n%s",
        df.shape,
        df[TARGET_COLUMN].value_counts().to_string(),
    )
    return df


def split_data(
    df: pd.DataFrame,
    target_col: str = TARGET_COLUMN,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
           np.ndarray, np.ndarray, np.ndarray]:
    """
    Split the dataset into train / validation / test portions (70/15/15).

    Parameters
    ----------
    df : pd.DataFrame
        Full cleaned dataset (features + labels).
    target_col : str
        Name of the binary label column.

    Returns
    -------
    Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    # Separate features from target
    X = df.drop(columns=[target_col]).values
    y = df[target_col].values

    # First split: carve out the held-out test set (15 %)
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y,
        test_size=TEST_RATIO,
        random_state=RANDOM_SEED,
        stratify=y,        # Preserve class balance across splits
    )

    # Second split: split remainder into train (70 %) and validation (15 %)
    # Within the 85 % remainder, validation is 15/85 ≈ 17.6 %
    val_ratio_adjusted = VAL_RATIO / (TRAIN_RATIO + VAL_RATIO)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=val_ratio_adjusted,
        random_state=RANDOM_SEED,
        stratify=y_temp,
    )

    logger.info(
        "Data split complete → Train: %d | Val: %d | Test: %d",
        len(X_train), len(X_val), len(X_test),
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def get_feature_names(df: pd.DataFrame, target_col: str = TARGET_COLUMN) -> list:
    """Return list of feature column names (excluding the target)."""
    return [c for c in df.columns if c != target_col]
