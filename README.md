# Phishing URL Detection – ML Project
**UEL EUE | Level 4 Cybersecurity | 48-Feature Kaggle Dataset**

---

## Quick Start

```powershell
# ⚠️  Windows PowerShell: use "python -m pip" instead of bare "pip"

# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Place your dataset
#    Download from Kaggle → data/raw/phishing_dataset.csv

# 3. Run just EDA (generates 8 figures)
python main.py --eda-only --data data/raw/phishing_dataset.csv

# 4. Run full pipeline (EDA + all 5 models)
python main.py --data data/raw/phishing_dataset.csv

# 5. Run unit tests
python -m pytest tests/ -v
```

---

## Project Structure

```
project/
├── data/
│   ├── raw/                    ← Place Kaggle CSV here
│   └── processed/              ← Auto-generated cleaned splits
├── src/
│   ├── preprocessing/
│   │   ├── data_loader.py      ← Load dataset + 70/15/15 split
│   │   └── preprocessor.py     ← Impute, scale, encode labels
│   └── models/
│       └── trainer.py          ← 5-model pipeline + evaluation
├── reports/
│   └── figures/                ← All 8 EDA plots + confusion matrices
├── models_saved/               ← .pkl files for each model
├── tests/
│   └── test_pipeline.py        ← 9 unit tests (all passing)
├── eda.py                      ← Standalone EDA script
├── main.py                     ← Master pipeline entry-point
└── requirements.txt
```

---

## EDA Figures Generated

| # | File | Description |
|---|------|-------------|
| 1 | `01_class_distribution_pie.png` | Donut chart of class balance |
| 2 | `02_class_distribution_bar.png` | Bar chart with counts + % |
| 3 | `03_correlation_heatmap.png` | Top-20 feature correlations |
| 4 | `04_feature_histograms.png` | UrlLength + NumDots distributions |
| 5 | `05_boxplots.png` | Phishing vs. Legitimate boxplots |
| 6 | `06_missing_value_matrix.png` | Missing data visualisation |
| 7 | `07_feature_importance.png` | ExtraTrees importance ranking |
| 8 | `08_pairplot_top_features.png` | Top-5 feature pairplot |

---

## Models & Hyperparameter Search

| Model | Key Tuned Params | CV Folds | N Iterations |
|-------|-----------------|----------|-------------|
| Logistic Regression | C, class_weight | 5 | 20 |
| Random Forest | n_estimators, max_depth, features | 5 | 20 |
| XGBoost | learning_rate, depth, subsample | 5 | 20 |
| Decision Tree | max_depth, criterion, leaf size | 5 | 20 |
| MLP Neural Net | hidden_layer_sizes, alpha, lr | 5 | 20 |

**Split: 70% train / 15% validation / 15% held-out test** (stratified)

---

## Expected Dataset Format

The Kaggle Phishing URL dataset should have:
- **48 numeric feature columns** (pre-extracted URL features)
- **1 label column** named `Result` with values `{-1, 1}`
  - `1`  = Phishing
  - `-1` = Legitimate

Labels are auto-remapped to `{0, 1}` during preprocessing.
