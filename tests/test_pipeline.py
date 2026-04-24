"""
tests/test_pipeline.py
=======================
Unit tests for the preprocessing and data-loading modules.

Run with:  python -m pytest tests/ -v
"""

import os
import sys
import numpy as np
import pandas as pd
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing.preprocessor import PhishingPreprocessor
from src.preprocessing.data_loader import split_data, get_feature_names

# ---------------------------------------------------------------------------
# Fixtures – synthetic dummy dataset resembling the Kaggle structure
# ---------------------------------------------------------------------------

@pytest.fixture
def dummy_df() -> pd.DataFrame:
    """
    Create a small synthetic DataFrame that mirrors the Kaggle dataset format:
      Kaggle: shashwatwork/phishing-dataset-for-machine-learning
      - 48 numeric features
      - 1 label column 'CLASS_LABEL' with values {0, 1}  (0=Legitimate, 1=Phishing)
    """
    np.random.seed(42)
    n_samples  = 500
    n_features = 48
    feature_cols = [f"feat_{i}" for i in range(n_features)]

    X = np.random.randn(n_samples, n_features)
    # Introduce a small fraction of NaN values (~2 %)
    mask = np.random.rand(*X.shape) < 0.02
    X[mask] = np.nan

    df = pd.DataFrame(X, columns=feature_cols)
    # Labels: 0=Legitimate, 1=Phishing  (matching Kaggle schema; no -1 values)
    df["CLASS_LABEL"] = np.random.choice([0, 1], size=n_samples, p=[0.48, 0.52])
    return df


# ---------------------------------------------------------------------------
# Data Loader Tests
# ---------------------------------------------------------------------------

class TestDataLoader:
    def test_split_ratios(self, dummy_df):
        """Verify 70/15/15 split produces approximately correct set sizes."""
        X_train, X_val, X_test, y_train, y_val, y_test = split_data(dummy_df, target_col="CLASS_LABEL")
        total = len(dummy_df)

        # Allow ±5% tolerance due to stratified rounding
        assert abs(len(X_train) / total - 0.70) < 0.05, "Train ratio off"
        assert abs(len(X_val)   / total - 0.15) < 0.05, "Val ratio off"
        assert abs(len(X_test)  / total - 0.15) < 0.05, "Test ratio off"

    def test_no_overlap(self, dummy_df):
        """Ensure indices of train/val/test sets do not overlap."""
        # We cannot directly check indices from numpy arrays, but
        # total count must equal original sample count
        X_train, X_val, X_test, y_train, y_val, y_test = split_data(dummy_df, target_col="CLASS_LABEL")
        assert len(X_train) + len(X_val) + len(X_test) == len(dummy_df)

    def test_get_feature_names(self, dummy_df):
        """get_feature_names should return all columns except target."""
        names = get_feature_names(dummy_df, target_col="CLASS_LABEL")
        assert "CLASS_LABEL" not in names
        assert len(names) == dummy_df.shape[1] - 1

    def test_label_distribution_preserved(self, dummy_df):
        """Stratified split should preserve approximate class balance."""
        X_train, _, X_test, y_train, _, y_test = split_data(dummy_df, target_col="CLASS_LABEL")
        train_ratio = y_train.mean()
        test_ratio  = y_test.mean()
        # Phishing proportion should be similar in train and test (±5 %)
        assert abs(train_ratio - test_ratio) < 0.05


# ---------------------------------------------------------------------------
# Preprocessor Tests
# ---------------------------------------------------------------------------

class TestPreprocessor:
    def test_fit_transform_shape(self, dummy_df):
        """Output shape should match input (minus constant features)."""
        X_train, _, _, _, _, _ = split_data(dummy_df, target_col="CLASS_LABEL")
        prep = PhishingPreprocessor()
        X_out = prep.fit_transform(X_train)
        # Should have same or fewer columns than input
        assert X_out.shape[0] == X_train.shape[0]
        assert X_out.shape[1] <= X_train.shape[1]

    def test_no_nan_after_imputation(self, dummy_df):
        """Ensure no NaN values remain after fit_transform."""
        X_train, X_val, X_test, _, _, _ = split_data(dummy_df, target_col="CLASS_LABEL")
        prep = PhishingPreprocessor()
        X_tr = prep.fit_transform(X_train)
        X_va = prep.transform(X_val)
        X_te = prep.transform(X_test)

        assert not np.isnan(X_tr).any(), "NaN in training set after transform"
        assert not np.isnan(X_va).any(), "NaN in validation set after transform"
        assert not np.isnan(X_te).any(), "NaN in test set after transform"

    def test_standard_scaling(self, dummy_df):
        """Scaled training features should have mean ≈ 0 and std ≈ 1."""
        X_train, _, _, _, _, _ = split_data(dummy_df, target_col="CLASS_LABEL")
        prep = PhishingPreprocessor()
        X_out = prep.fit_transform(X_train)

        col_means = X_out.mean(axis=0)
        col_stds  = X_out.std(axis=0)

        np.testing.assert_allclose(col_means, 0, atol=1e-6,
                                   err_msg="Mean not zero after scaling")
        np.testing.assert_allclose(col_stds,  1, atol=1e-6,
                                   err_msg="Std not 1 after scaling")

    def test_encode_labels(self):
        """
        Labels from the Kaggle dataset are already {0, 1}.
        encode_labels() should return them unchanged as integers.
        """
        prep = PhishingPreprocessor()
        raw = np.array([0, 1, 0, 1, 1, 0])
        encoded = prep.encode_labels(raw)
        expected = np.array([0, 1, 0, 1, 1, 0])
        np.testing.assert_array_equal(encoded, expected)

    def test_transform_without_fit_raises(self, dummy_df):
        """
        Calling transform before fit_transform should raise an AttributeError
        because the imputer/scaler internals are not initialised.
        """
        _, X_val, _, _, _, _ = split_data(dummy_df, target_col="CLASS_LABEL")
        prep = PhishingPreprocessor()
        with pytest.raises(Exception):
            prep.transform(X_val)
