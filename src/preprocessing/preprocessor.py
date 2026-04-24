"""
src/preprocessing/preprocessor.py
===================================
Cleaning and transformation pipeline for the Phishing URL dataset.

Dataset source
--------------
  Kaggle – "Phishing Dataset for Machine Learning" by Shashwat Tiwari
  https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning
  Labels: 'CLASS_LABEL' column  →  1 = Phishing,  0 = Legitimate  (already binary; no remapping needed)

Steps performed
---------------
1. Handle missing values (median imputation for numeric features).
2. Remove zero-variance (constant) features.
3. Scale numeric features with StandardScaler (fit on train only – prevents data leakage).
4. Save the processed datasets to data/processed/.
"""

import logging
import os
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

PROCESSED_DIR = "data/processed"


class PhishingPreprocessor:
    """
    Stateful preprocessing pipeline.

    The preprocessor is *fit* on training data only, then applied
    (transform) to validation and test sets to prevent data leakage.
    """

    def __init__(self) -> None:
        # Median imputer handles rare NaN entries in numeric features
        self._imputer = SimpleImputer(strategy="median")
        # StandardScaler normalises feature magnitudes for linear models
        self._scaler = StandardScaler()
        self._constant_cols: list[int] = []   # Indices of dropped columns
        self._feature_names: Optional[list[str]] = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fit_transform(
        self, X: np.ndarray, feature_names: Optional[list] = None
    ) -> np.ndarray:
        """
        Fit the pipeline on training data and return the transformed array.

        Parameters
        ----------
        X : np.ndarray  Shape (n_train, n_features)
        feature_names : list, optional  Column names for logging.

        Returns
        -------
        np.ndarray  Cleaned, scaled training feature matrix.
        """
        self._feature_names = feature_names

        # Step 1 – Impute missing values
        X = self._imputer.fit_transform(X)
        logger.info("Imputation complete.")

        # Step 2 – Drop constant (zero-variance) features
        variances = X.var(axis=0)
        self._constant_cols = list(np.where(variances == 0)[0])
        if self._constant_cols:
            logger.warning(
                "Dropping %d constant feature(s): indices %s",
                len(self._constant_cols), self._constant_cols,
            )
        X = np.delete(X, self._constant_cols, axis=1)

        # Step 3 – Fit + apply StandardScaler
        X = self._scaler.fit_transform(X)
        logger.info("Scaling complete. Output shape: %s", X.shape)
        return X

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Apply the already-fitted pipeline to new data (val / test).

        Parameters
        ----------
        X : np.ndarray  Raw feature matrix.

        Returns
        -------
        np.ndarray  Cleaned, scaled feature matrix.
        """
        X = self._imputer.transform(X)
        X = np.delete(X, self._constant_cols, axis=1)
        X = self._scaler.transform(X)
        return X

    def encode_labels(self, y: np.ndarray) -> np.ndarray:
        """
        Validate and return the label array.

        The Kaggle dataset (shashwatwork/phishing-dataset-for-machine-learning)
        already uses binary labels:  0 = Legitimate,  1 = Phishing.
        No remapping is required.  This method is kept for pipeline
        consistency and logs a warning if unexpected values are found.

        Parameters
        ----------
        y : np.ndarray  Raw label array (expected values: {0, 1}).

        Returns
        -------
        np.ndarray  Integer label array {0, 1}.
        """
        unique_vals = set(np.unique(y).tolist())
        expected = {0, 1}
        unexpected = unique_vals - expected
        if unexpected:
            logger.warning(
                "Unexpected label values found: %s. "
                "Expected only {0, 1} from the Kaggle dataset. "
                "Check that you are using shashwatwork/phishing-dataset-for-machine-learning.",
                unexpected,
            )
        return y.astype(int)

    def save(self, filepath: str) -> None:
        """Save the fitted preprocessor to a pickle file."""
        import joblib
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)
        logger.info("Saved preprocessor to %s", filepath)

    @classmethod
    def load(cls, filepath: str) -> "PhishingPreprocessor":
        """Load a fitted preprocessor from a pickle file."""
        import joblib
        logger.info("Loading preprocessor from %s", filepath)
        return joblib.load(filepath)


def save_processed_splits(
    splits: Tuple,
    feature_names: list,
    output_dir: str = PROCESSED_DIR,
) -> None:
    """
    Persist the train/val/test splits as CSV files in data/processed/.

    Parameters
    ----------
    splits : Tuple  (X_train, X_val, X_test, y_train, y_val, y_test)
    feature_names : list  Column names for the feature DataFrame.
    output_dir : str  Destination directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    X_train, X_val, X_test, y_train, y_val, y_test = splits
    subsets = {
        "train": (X_train, y_train),
        "val":   (X_val,   y_val),
        "test":  (X_test,  y_test),
    }
    for name, (X, y) in subsets.items():
        # Combine features and labels into a single CSV
        df_out = pd.DataFrame(X, columns=feature_names[:X.shape[1]])
        df_out["label"] = y
        path = os.path.join(output_dir, f"{name}.csv")
        df_out.to_csv(path, index=False)
        logger.info("Saved %s split → %s  (%d rows)", name, path, len(df_out))
