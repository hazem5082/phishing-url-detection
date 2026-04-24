"""
src/models/trainer.py
======================
Five-model training pipeline for Phishing URL Detection.

Models compared
---------------
  1. Logistic Regression    – Linear baseline
  2. Random Forest          – Ensemble of decision trees
  3. XGBoost                – Gradient-boosted trees (state-of-the-art tabular)
  4. Decision Tree          – Interpretable single-tree model
  5. Multi-Layer Perceptron – Neural network (sklearn implementation)

Pipeline
--------
  • RandomizedSearchCV over a held-out validation fold for hyperparameter tuning
  • Best estimator re-trained on full train set
  • Serialisation to models_saved/<model_name>.pkl via joblib
  • Per-model Classification Report + Confusion Matrix
"""

import logging
import os
import time
import warnings
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import RandomizedSearchCV
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

try:
    from xgboost import XGBClassifier
    _XGBOOST_AVAILABLE = True
except ImportError:
    _XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not installed; substituting GradientBoostingClassifier.")
    from sklearn.ensemble import GradientBoostingClassifier

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODELS_DIR   = "models_saved"
FIGURES_DIR  = "reports/figures"
RANDOM_SEED  = 42
CV_FOLDS     = 5       # Cross-validation folds inside RandomizedSearchCV
N_ITER       = 20      # Number of random hyperparameter combinations to try
SCORING      = "f1"    # Optimise for F1 – balances precision and recall

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Hyperparameter search spaces
# ---------------------------------------------------------------------------

def _search_spaces() -> Dict[str, Tuple[Any, Dict]]:
    """
    Define each model and its hyperparameter space for RandomizedSearchCV.

    Returns a dict mapping model name → (estimator, param_distributions).
    Ranges are chosen to be meaningful yet computationally tractable within
    an academic 48-hour window.
    """
    spaces = {
        # ------------------------------------------------------------------
        # 1. Logistic Regression – baseline linear classifier
        # ------------------------------------------------------------------
        "Logistic_Regression": (
            LogisticRegression(
                max_iter=2000,
                random_state=RANDOM_SEED,
                solver="lbfgs",
                n_jobs=-1,
            ),
            {
                "C":         [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
                "penalty":   ["l2"],      # l1 not supported for lbfgs
                "class_weight": [None, "balanced"],
            },
        ),

        # ------------------------------------------------------------------
        # 2. Random Forest – powerful ensemble; resistant to overfitting
        # ------------------------------------------------------------------
        "Random_Forest": (
            RandomForestClassifier(
                random_state=RANDOM_SEED,
                n_jobs=-1,
            ),
            {
                "n_estimators":      [100, 200, 300, 500],
                "max_depth":         [None, 10, 20, 30, 40],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf":  [1, 2, 4],
                "max_features":      ["sqrt", "log2"],
                "class_weight":      [None, "balanced"],
            },
        ),

        # ------------------------------------------------------------------
        # 3. XGBoost – gradient-boosted trees; typically best on tabular data
        # ------------------------------------------------------------------
        "XGBoost": (
            (
                XGBClassifier(
                    eval_metric="logloss",
                    random_state=RANDOM_SEED,
                    n_jobs=-1,
                    verbosity=0,
                    use_label_encoder=False,
                )
                if _XGBOOST_AVAILABLE
                else GradientBoostingClassifier(random_state=RANDOM_SEED)
            ),
            {
                "n_estimators":       [100, 200, 300],
                "max_depth":          [3, 5, 7, 9],
                "learning_rate":      [0.01, 0.05, 0.1, 0.2],
                "subsample":          [0.6, 0.8, 1.0],
                "colsample_bytree":   [0.6, 0.8, 1.0],
                "gamma":              [0, 0.1, 0.5, 1.0],
                "reg_alpha":          [0, 0.1, 1.0],
                "reg_lambda":         [1.0, 2.0, 5.0],
            },
        ),

        # ------------------------------------------------------------------
        # 4. Decision Tree – highly interpretable; good for explainability
        # ------------------------------------------------------------------
        "Decision_Tree": (
            DecisionTreeClassifier(
                random_state=RANDOM_SEED,
            ),
            {
                "max_depth":          [None, 5, 10, 15, 20, 25],
                "min_samples_split":  [2, 5, 10, 20],
                "min_samples_leaf":   [1, 2, 4, 8],
                "criterion":          ["gini", "entropy"],
                "class_weight":       [None, "balanced"],
            },
        ),

        # ------------------------------------------------------------------
        # 5. MLP – neural network; can learn non-linear feature interactions
        # ------------------------------------------------------------------
        "MLP": (
            MLPClassifier(
                max_iter=500,
                early_stopping=True,      # Prevent overfitting
                validation_fraction=0.1,
                random_state=RANDOM_SEED,
            ),
            {
                "hidden_layer_sizes": [
                    (64,), (128,), (256,),
                    (128, 64), (256, 128), (256, 128, 64),
                ],
                "activation":   ["relu", "tanh"],
                "alpha":        [1e-5, 1e-4, 1e-3, 1e-2],
                "learning_rate_init": [1e-4, 1e-3, 5e-3],
                "batch_size":   [64, 128, 256],
            },
        ),
    }
    return spaces


# ---------------------------------------------------------------------------
# Core training function
# ---------------------------------------------------------------------------

def train_model(
    name: str,
    estimator: Any,
    param_dist: Dict,
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> Any:
    """
    Run RandomizedSearchCV to find the best hyperparameters, then return
    the best estimator already fitted on the full training set.

    Parameters
    ----------
    name       : Model display name for logging.
    estimator  : Sklearn-compatible estimator instance.
    param_dist : Dictionary of hyperparameter distributions.
    X_train    : Feature matrix (training split).
    y_train    : Label vector (training split).

    Returns
    -------
    Best fitted estimator from RandomizedSearchCV.
    """
    logger.info("Training [%s] …", name)
    t0 = time.perf_counter()

    search = RandomizedSearchCV(
        estimator=estimator,
        param_distributions=param_dist,
        n_iter=N_ITER,
        scoring=SCORING,
        cv=CV_FOLDS,
        refit=True,              # Refit best params on full training data
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbose=0,
    )
    search.fit(X_train, y_train)

    elapsed = time.perf_counter() - t0
    logger.info(
        "[%s] done in %.1fs  |  Best %s: %.4f  |  Best params: %s",
        name, elapsed, SCORING, search.best_score_, search.best_params_,
    )
    return search.best_estimator_


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def evaluate_model(
    name: str,
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    split_label: str = "Test",
) -> Dict[str, Any]:
    """
    Compute and print Classification Report; save Confusion Matrix figure.

    Parameters
    ----------
    name        : Model name for display and filename.
    model       : Fitted sklearn estimator.
    X           : Feature matrix.
    y           : True labels.
    split_label : 'Validation' or 'Test' – used in titles and filenames.

    Returns
    -------
    dict  Keys: accuracy, report (str), cm (ndarray).
    """
    y_pred = model.predict(X)
    cm     = confusion_matrix(y, y_pred)
    report = classification_report(
        y, y_pred,
        target_names=["Legitimate (0)", "Phishing (1)"],
        digits=4,
    )
    accuracy = (y == y_pred).mean()

    print(f"\n{'=' * 60}")
    print(f"  Model : {name}  [{split_label}]")
    print(f"{'=' * 60}")
    print(report)

    # --- Confusion Matrix Plot ---
    fig, ax = plt.subplots(figsize=(5, 4))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Legitimate", "Phishing"],
    )
    disp.plot(
        cmap="Blues",
        ax=ax,
        colorbar=False,
        values_format="d",
    )
    ax.set_title(f"Confusion Matrix – {name}\n({split_label})", fontweight="bold")
    # Remove default xlabel/ylabel for cleaner look
    ax.set_xlabel("Predicted Label", labelpad=8)
    ax.set_ylabel("True Label", labelpad=8)

    fig_path = os.path.join(
        FIGURES_DIR,
        f"cm_{name.lower().replace(' ', '_')}_{split_label.lower()}.png",
    )
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("  Confusion matrix saved → %s", fig_path)

    return {"accuracy": accuracy, "report": report, "cm": cm}


def save_model(model: Any, name: str) -> str:
    """
    Serialise model to disk using joblib.

    Parameters
    ----------
    model : Fitted estimator.
    name  : Human-readable name (used as filename base).

    Returns
    -------
    Absolute path of the saved .pkl file.
    """
    filename = name.lower().replace(" ", "_") + ".pkl"
    path = os.path.join(MODELS_DIR, filename)
    joblib.dump(model, path, compress=3)   # compress=3 reduces file size ~50 %
    logger.info("Model saved → %s", path)
    return path


# ---------------------------------------------------------------------------
# Summary comparison table
# ---------------------------------------------------------------------------

def print_comparison_table(results: List[Dict]) -> None:
    """
    Print a side-by-side comparison table of all model metrics.

    Parameters
    ----------
    results : List of dicts, each with keys: name, accuracy, report.
    """
    print("\n" + "=" * 70)
    print(" MODEL COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Model':<25} {'Accuracy':>10} {'F1 (Phishing)':>16}")
    print("-" * 55)
    for r in results:
        # Extract phishing-class F1 from classification report string
        lines = r["report"].strip().split("\n")
        phish_f1 = "N/A"
        for line in lines:
            if "Phishing" in line:
                parts = line.split()
                phish_f1 = parts[3] if len(parts) >= 4 else "N/A"
                break
        print(f"{r['name']:<25} {r['accuracy']:>10.4f} {phish_f1:>16}")
    print("=" * 70 + "\n")


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_all_models(
    X_train: np.ndarray,
    X_val:   np.ndarray,
    X_test:  np.ndarray,
    y_train: np.ndarray,
    y_val:   np.ndarray,
    y_test:  np.ndarray,
) -> List[Dict]:
    """
    Train, tune, evaluate, and save all 5 models.

    Parameters
    ----------
    X_train, X_val, X_test : Feature matrices for each split.
    y_train, y_val, y_test : Label arrays for each split.

    Returns
    -------
    List of result dictionaries (one per model).
    """
    spaces  = _search_spaces()
    results = []

    for name, (estimator, param_dist) in spaces.items():
        # ---- 1. Hyperparameter search + training -------------------------
        best_model = train_model(name, estimator, param_dist, X_train, y_train)

        # ---- 2. Validation-set evaluation --------------------------------
        val_result  = evaluate_model(name, best_model, X_val,  y_val,  "Validation")

        # ---- 3. Held-out test evaluation ---------------------------------
        test_result = evaluate_model(name, best_model, X_test, y_test, "Test")

        # ---- 4. Serialise best model ------------------------------------
        save_model(best_model, name)

        results.append({
            "name":     name,
            "model":    best_model,
            "accuracy": test_result["accuracy"],
            "report":   test_result["report"],
            "cm":       test_result["cm"],
        })

    print_comparison_table(results)
    return results
