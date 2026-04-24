"""
download_dataset.py
====================
Downloads the Kaggle phishing dataset via kagglehub and copies
it to the expected location: data/raw/phishing_dataset.csv
"""

import shutil
import os
import kagglehub

print("Downloading dataset from Kaggle...")
path = kagglehub.dataset_download("shashwatwork/phishing-dataset-for-machine-learning")
print(f"Downloaded to: {path}")

# Find the CSV inside the downloaded folder
csv_files = [f for f in os.listdir(path) if f.endswith(".csv")]
if not csv_files:
    raise FileNotFoundError(f"No CSV found in {path}")

src = os.path.join(path, csv_files[0])
print(f"Found CSV: {src}")

# Copy to the expected project location
dest_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(dest_dir, exist_ok=True)
dest = os.path.join(dest_dir, "phishing_dataset.csv")

shutil.copy2(src, dest)
print(f"\n[OK] Dataset ready at: {dest}")
print("You can now run: python main.py --data data/raw/phishing_dataset.csv")
