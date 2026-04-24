"""
setup_project.py
================
Project Initialization Script for Phishing URL Detection.
Creates the full directory structure required by the rubric and
generates placeholder __init__.py files for Python packages.

Author  : ML Engineer
Date    : 2026-04-24
Course  : Cybersecurity – UEL EUE (Level 4)
"""

import os
import sys


# ---------------------------------------------------------------------------
# Directory tree to create
# ---------------------------------------------------------------------------
DIRECTORIES = [
    "data/raw",           # Raw, unmodified Kaggle CSV files
    "data/processed",     # Cleaned & feature-engineered CSVs / arrays
    "src/preprocessing",  # Data cleaning and transformation modules
    "src/models",         # Model training and evaluation modules
    "notebooks",          # Jupyter notebooks for interactive exploration
    "tests",              # Unit tests for preprocessing and models
    "reports/figures",    # Saved plots / confusion matrices
    "models_saved",       # Serialised .pkl model artefacts
]


def create_directory_structure() -> None:
    """
    Iterates over DIRECTORIES and creates each one (including parents)
    if it does not already exist.
    """
    print("=" * 60)
    print(" Phishing URL Detection – Project Initialisation")
    print("=" * 60)

    for directory in DIRECTORIES:
        os.makedirs(directory, exist_ok=True)
        # Place an empty __init__.py in Python-package directories
        if directory.startswith("src") or directory == "tests":
            init_path = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_path):
                with open(init_path, "w") as f:
                    f.write(
                        f'"""Package: {directory.replace("/", ".")}"""\n'
                    )
        status = "✓ Created" if os.path.isdir(directory) else "✗ Failed "
        print(f"  {status}  {directory}/")

    print("\n✅  Directory structure ready.\n")


def create_requirements_file() -> None:
    """
    Writes a requirements.txt with all libraries needed for the project.
    """
    requirements = [
        "pandas>=1.5",
        "numpy>=1.23",
        "scikit-learn>=1.2",
        "xgboost>=1.7",
        "matplotlib>=3.6",
        "seaborn>=0.12",
        "joblib>=1.2",
        "missingno>=0.5",
        "imbalanced-learn>=0.10",
        "jupyter>=1.0",
        "ipykernel>=6.0",
    ]
    req_path = "requirements.txt"
    with open(req_path, "w") as f:
        f.write("\n".join(requirements) + "\n")
    print(f"  ✓ Created  {req_path}")


if __name__ == "__main__":
    # Change working directory to the script's location for consistency
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    create_directory_structure()
    create_requirements_file()
    print("\nRun the following to install dependencies:")
    print("   pip install -r requirements.txt\n")
    sys.exit(0)
