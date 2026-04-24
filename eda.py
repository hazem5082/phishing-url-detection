"""
eda.py
======
Exploratory Data Analysis for Phishing URL Detection.
Generates 8 publication-quality visualisations required for the rubric.

Dataset sources (assigned by UEL EUE)
--------------------------------------
  PRIMARY (this script):
    Kaggle – shashwatwork/phishing-dataset-for-machine-learning
    https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning
    10,000 rows | 48 features | label column: 'CLASS_LABEL' (1=Phishing, 0=Legitimate)

  REFERENCE (text/NLP, not used in this feature-based pipeline):
    HuggingFace – ealvaradob/phishing-dataset
    https://huggingface.co/datasets/ealvaradob/phishing-dataset
    Columns: 'text', 'label' (1=Phishing, 0=Benign)

  REFERENCE (live phishing URLs, phishing-only, no legitimate class):
    PhishTank developer download
    https://www.phishtank.com/developer_info.php
    Columns: phish_id, url, phish_detail_url, submission_time,
             verified, verification_time, online, target

Visualisations produced
-----------------------
  1. Class distribution  – Pie chart
  2. Class distribution  – Bar chart
  3. Correlation heatmap – Top 20 features correlated with label
  4. Feature histograms  – UrlLength and NumDots
  5. Boxplots            – UrlLength and NumDots vs. phishing / legitimate
  6. Missing value matrix (requires missingno)
  7. Feature importance ranking – ExtraTreesClassifier
  8. Pairplot            – Top 5 discriminating features

Usage
-----
    python eda.py --data data/raw/Phishing_Legitimate_full.csv
    python eda.py --data data/raw/Phishing_Legitimate_full.csv --target class
"""

import argparse
import logging
import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")            # Non-interactive backend (safe on all OS)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import ExtraTreesClassifier

warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global style – clean, academic-grade palette
# ---------------------------------------------------------------------------
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
PALETTE   = ["#2ecc71", "#e74c3c"]   # Green = legitimate, Red = phishing
FIGURE_DIR = "reports/figures"
os.makedirs(FIGURE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _save(fig: plt.Figure, filename: str) -> None:
    """Save figure to reports/figures/ and close it to free memory."""
    path = os.path.join(FIGURE_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved → %s", path)


def _label_name(val: int) -> str:
    """Convert numeric label to human-readable string.
    Kaggle dataset convention: 1 = Phishing, 0 = Legitimate.
    """
    return "Phishing" if val == 1 else "Legitimate"


# ===========================================================================
# 1.  CLASS DISTRIBUTION – PIE CHART
# ===========================================================================

def plot_class_pie(df: pd.DataFrame, target: str = "CLASS_LABEL") -> None:
    """
    Visualise class balance as a donut/pie chart.
    Imbalanced distributions directly impact model choice and metric selection.
    """
    counts = df[target].value_counts().sort_index()
    labels = [_label_name(v) for v in counts.index]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=labels,
        colors=PALETTE,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.80,
        wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(13)
        at.set_fontweight("bold")

    ax.set_title("Class Distribution (Phishing vs. Legitimate)", pad=20, fontweight="bold")
    ax.axis("equal")
    _save(fig, "01_class_distribution_pie.png")


# ===========================================================================
# 2.  CLASS DISTRIBUTION – BAR CHART
# ===========================================================================

def plot_class_bar(df: pd.DataFrame, target: str = "CLASS_LABEL") -> None:
    """
    Bar chart of class frequencies – complements the pie chart with exact counts.
    """
    counts = df[target].value_counts().sort_index()
    labels = [_label_name(v) for v in counts.index]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, counts.values, color=PALETTE, edgecolor="white", linewidth=1.2, width=0.5)

    # Annotate each bar with the count and percentage
    total = counts.sum()
    for bar, count in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + total * 0.005,
            f"{count:,}\n({count / total:.1%})",
            ha="center", va="bottom", fontsize=11, fontweight="bold",
        )

    ax.set_title("Class Distribution – Count", fontweight="bold")
    ax.set_ylabel("Sample Count")
    ax.set_ylim(0, max(counts.values) * 1.15)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, "02_class_distribution_bar.png")


# ===========================================================================
# 3.  CORRELATION HEATMAP – TOP 20 FEATURES
# ===========================================================================

def plot_correlation_heatmap(df: pd.DataFrame, target: str = "CLASS_LABEL", top_n: int = 20) -> None:
    """
    Pearson correlation heatmap of the top-N features most correlated
    with the label.  Reveals multicollinearity and feature redundancy.
    """
    # Select the 20 features with highest absolute correlation to target
    numeric_df = df.select_dtypes(include=np.number)
    correlations = numeric_df.corr()[target].abs().sort_values(ascending=False)
    top_features = correlations.iloc[1:top_n + 1].index.tolist()
    subset = df[top_features + [target]]

    corr_matrix = subset.corr()

    fig, ax = plt.subplots(figsize=(14, 11))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # Show lower triangle only
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=0,
        linewidths=0.4,
        vmin=-1, vmax=1,
        ax=ax,
        annot_kws={"size": 7},
    )
    ax.set_title(f"Correlation Heatmap – Top {top_n} Features", fontweight="bold", pad=15)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    _save(fig, "03_correlation_heatmap.png")


# ===========================================================================
# 4.  FEATURE DISTRIBUTION HISTOGRAMS – UrlLength & NumDots
# ===========================================================================

def plot_feature_histograms(df: pd.DataFrame, target: str = "CLASS_LABEL") -> None:
    """
    Overlapping histograms showing per-class distributions of key URL features.
    UrlLength and NumDots are among the most intuitive phishing indicators.
    """
    # Map column names gracefully (dataset uses different capitalisation styles)
    col_map = {c.lower(): c for c in df.columns}
    features_to_plot = ["urllength", "numdots"]
    found_features = [col_map[f] for f in features_to_plot if f in col_map]

    if not found_features:
        logger.warning("UrlLength / NumDots columns not found; skipping histogram plot.")
        return

    fig, axes = plt.subplots(1, len(found_features), figsize=(7 * len(found_features), 5))
    if len(found_features) == 1:
        axes = [axes]

    for ax, feat in zip(axes, found_features):
        for label_val, color in zip(sorted(df[target].unique()), PALETTE):
            subset = df[df[target] == label_val][feat].dropna()
            ax.hist(
                subset,
                bins=40,
                alpha=0.65,
                color=color,
                label=_label_name(label_val),
                edgecolor="white",
                linewidth=0.4,
            )
        ax.set_xlabel(feat, fontweight="bold")
        ax.set_ylabel("Frequency")
        ax.set_title(f"Distribution of {feat}", fontweight="bold")
        ax.legend(framealpha=0.8)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Feature Distributions by Class", fontweight="bold", y=1.02)
    _save(fig, "04_feature_histograms.png")


# ===========================================================================
# 5.  BOXPLOTS – UrlLength & NumDots vs. Class
# ===========================================================================

def plot_boxplots(df: pd.DataFrame, target: str = "CLASS_LABEL") -> None:
    """
    Boxplots reveal median shift, IQR spread, and outliers between classes.
    A clear median separation indicates high individual feature discriminability.
    """
    col_map = {c.lower(): c for c in df.columns}
    features_to_plot = ["urllength", "numdots"]
    found_features = [col_map[f] for f in features_to_plot if f in col_map]

    if not found_features:
        logger.warning("UrlLength / NumDots not found; using top 2 numeric features.")
        numerics = df.select_dtypes(include=np.number).columns.tolist()
        found_features = [c for c in numerics if c != target][:2]

    # Add a readable label column for Seaborn grouping
    df_plot = df.copy()
    df_plot["CLASS_LABEL"] = df_plot[target].map({1: "Phishing", 0: "Legitimate"})

    fig, axes = plt.subplots(1, len(found_features), figsize=(7 * len(found_features), 5))
    if len(found_features) == 1:
        axes = [axes]

    for ax, feat in zip(axes, found_features):
        sns.boxplot(
            data=df_plot,
            x="CLASS_LABEL",
            y=feat,
            palette={"Legitimate": PALETTE[0], "Phishing": PALETTE[1]},
            linewidth=1.2,
            flierprops={"marker": "o", "markersize": 3, "alpha": 0.4},
            ax=ax,
        )
        ax.set_title(f"{feat} by Class", fontweight="bold")
        ax.set_xlabel("")
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Boxplots: Phishing vs. Legitimate", fontweight="bold", y=1.02)
    _save(fig, "05_boxplots.png")


# ===========================================================================
# 6.  MISSING VALUE MATRIX
# ===========================================================================

def plot_missing_values(df: pd.DataFrame) -> None:
    """
    Visualise missing-data patterns using missingno's matrix plot.
    Identifies whether missingness is random or follows a pattern.
    Falls back to a simple bar chart if missingno is unavailable.
    """
    try:
        import missingno as msno

        fig, ax = plt.subplots(figsize=(14, 6))
        msno.matrix(df, ax=ax, sparkline=False, color=(0.18, 0.45, 0.71))
        ax.set_title("Missing Value Matrix", fontweight="bold", pad=12)
        _save(fig, "06_missing_value_matrix.png")

    except ImportError:
        logger.warning("missingno not installed; using fallback bar chart.")
        missing = df.isnull().sum()
        missing = missing[missing > 0]

        fig, ax = plt.subplots(figsize=(10, 5))
        if missing.empty:
            ax.text(
                0.5, 0.5,
                "No Missing Values Found ✓",
                ha="center", va="center",
                fontsize=16, color="green", fontweight="bold",
                transform=ax.transAxes,
            )
        else:
            missing.plot(kind="bar", ax=ax, color="#3498db", edgecolor="white")
            ax.set_ylabel("Missing Count")
            ax.set_title("Missing Values per Feature", fontweight="bold")

        _save(fig, "06_missing_value_matrix.png")


# ===========================================================================
# 7.  FEATURE IMPORTANCE RANKING
# ===========================================================================

def plot_feature_importance(df: pd.DataFrame, target: str = "CLASS_LABEL", top_n: int = 20) -> None:
    """
    Rank features by impurity-based importance from an ExtraTreesClassifier.
    Provides a quick, model-driven assessment of discriminative power.
    ExtraTrees is used (faster than Random Forest) – see Geurts et al. 2006.
    """
    X = df.drop(columns=[target]).select_dtypes(include=np.number)
    y = df[target].values
    feature_names = X.columns.tolist()

    clf = ExtraTreesClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X.values, y)

    importances = pd.Series(clf.feature_importances_, index=feature_names)
    importances = importances.nlargest(top_n).sort_values()

    fig, ax = plt.subplots(figsize=(9, 8))
    colors = sns.color_palette("YlOrRd", len(importances))
    importances.plot(kind="barh", ax=ax, color=colors, edgecolor="white")
    ax.set_title(f"Top {top_n} Feature Importances (ExtraTrees)", fontweight="bold")
    ax.set_xlabel("Mean Decrease in Impurity")
    ax.spines[["top", "right"]].set_visible(False)

    # Grid lines for readability
    ax.xaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    _save(fig, "07_feature_importance.png")


# ===========================================================================
# 8.  PAIRPLOT – TOP 5 DISCRIMINATING FEATURES
# ===========================================================================

def plot_pairplot(df: pd.DataFrame, target: str = "CLASS_LABEL", top_n: int = 5) -> None:
    """
    Seaborn pairplot for the top-N features most correlated with the label.
    Reveals linear separability and potential interaction effects.
    """
    numeric_df = df.select_dtypes(include=np.number)
    correlations = numeric_df.corr()[target].abs().sort_values(ascending=False)
    top_features = correlations.iloc[1:top_n + 1].index.tolist()

    df_plot = df[top_features + [target]].copy()
    df_plot["CLASS_LABEL"] = df_plot[target].map({1: "Phishing", -1: "Legitimate", 0: "Legitimate"})

    g = sns.pairplot(
        df_plot,
        hue="CLASS_LABEL",
        vars=top_features,
        palette={"Legitimate": PALETTE[0], "Phishing": PALETTE[1]},
        diag_kind="kde",
        plot_kws={"alpha": 0.4, "s": 15},
        corner=True,           # Show only lower triangle to reduce clutter
    )
    g.fig.suptitle(f"Pairplot – Top {top_n} Discriminating Features", y=1.02, fontweight="bold")
    _save(g.fig, "08_pairplot_top_features.png")


# ===========================================================================
# SUMMARY STATISTICS
# ===========================================================================

def print_summary(df: pd.DataFrame, target: str = "Result") -> None:
    """Print dataset summary statistics to stdout for quick review."""
    print("\n" + "=" * 60)
    print(" DATASET SUMMARY")
    print("=" * 60)
    print(f"  Shape        : {df.shape}")
    print(f"  Features     : {df.shape[1] - 1}")
    print(f"  Missing vals : {df.isnull().sum().sum()}")
    print(f"  Target map   : {dict(df[target].value_counts())}")
    print(f"  Dtypes       : {dict(df.dtypes.value_counts())}")
    print("=" * 60 + "\n")
    print(df.describe().T.to_string())
    print()


# ===========================================================================
# ENTRY POINT
# ===========================================================================

def run_eda(filepath: str, target: str = "CLASS_LABEL") -> None:
    """
    Orchestrate all 8 EDA visualisations.

    Parameters
    ----------
    filepath : str  Path to raw dataset CSV.
    target   : str  Label column name.
    """
    logger.info("Starting EDA pipeline …")
    df = pd.read_csv(filepath)

    print_summary(df, target)

    # Generate all 8 plots sequentially
    plot_class_pie(df, target)
    plot_class_bar(df, target)
    plot_correlation_heatmap(df, target)
    plot_feature_histograms(df, target)
    plot_boxplots(df, target)
    plot_missing_values(df)
    plot_feature_importance(df, target)
    plot_pairplot(df, target)

    logger.info("EDA complete. All figures saved to '%s/'.", FIGURE_DIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phishing URL EDA")
    parser.add_argument(
        "--data",
        default="data/raw/Phishing_Legitimate_full.csv",
        help="Path to raw dataset CSV (default: data/raw/Phishing_Legitimate_full.csv)",
    )
    parser.add_argument(
        "--target",
        default="CLASS_LABEL",
        help="Name of the label column (default: class)",
    )
    args = parser.parse_args()
    run_eda(args.data, args.target)
