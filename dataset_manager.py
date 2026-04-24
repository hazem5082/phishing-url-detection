"""
dataset_manager.py
==================
Production-grade dataset management with automatic Kaggle download,
validation, and caching.
"""

import os
import shutil
import logging
from pathlib import Path
import kagglehub

from config import (
    DATA_RAW_DIR,
    DATASET_PATH,
    KAGGLE_DATASET,
    AUTO_DOWNLOAD_DATASET,
)

logger = logging.getLogger(__name__)


class DatasetManager:
    """Manages dataset download, validation, and organization."""

    def __init__(self, dataset_path=DATASET_PATH, auto_download=AUTO_DOWNLOAD_DATASET):
        """
        Initialize the dataset manager.

        Parameters
        ----------
        dataset_path : Path
            Target location for the dataset CSV
        auto_download : bool
            If True, automatically download dataset if not found
        """
        self.dataset_path = Path(dataset_path)
        self.auto_download = auto_download

    def dataset_exists(self) -> bool:
        """Check if dataset already exists."""
        return self.dataset_path.exists()

    def download_dataset(self) -> Path:
        """
        Download the Kaggle phishing dataset.

        Returns
        -------
        Path
            Path to the downloaded dataset file

        Raises
        ------
        RuntimeError
            If download fails or no CSV found
        """
        logger.info(f"Downloading dataset: {KAGGLE_DATASET}")
        try:
            # Download via kagglehub
            path = kagglehub.dataset_download(KAGGLE_DATASET)
            logger.info(f"Downloaded to: {path}")

            # Find CSV file in the downloaded folder
            csv_files = list(Path(path).glob("*.csv"))
            if not csv_files:
                raise RuntimeError(f"No CSV files found in downloaded dataset: {path}")

            src_file = csv_files[0]
            logger.info(f"Found dataset: {src_file.name}")

            # Ensure destination directory exists
            self.dataset_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy to project location
            shutil.copy2(str(src_file), str(self.dataset_path))
            logger.info(f"Dataset copied to: {self.dataset_path}")

            return self.dataset_path

        except Exception as exc:
            logger.error(f"Dataset download failed: {exc}")
            raise RuntimeError(f"Failed to download dataset: {exc}") from exc

    def ensure_dataset(self) -> Path:
        """
        Ensure dataset is available, downloading if necessary.

        Returns
        -------
        Path
            Path to the dataset file

        Raises
        ------
        FileNotFoundError
            If dataset doesn't exist and auto_download is False
        RuntimeError
            If download fails
        """
        if self.dataset_exists():
            logger.debug(f"Dataset already exists: {self.dataset_path}")
            return self.dataset_path

        if not self.auto_download:
            raise FileNotFoundError(
                f"Dataset not found at {self.dataset_path} and auto_download is False. "
                f"Run: python download_dataset.py"
            )

        logger.info("Dataset not found. Attempting auto-download...")
        return self.download_dataset()


def setup_dataset() -> Path:
    """
    Convenience function to ensure dataset is ready.

    Returns
    -------
    Path
        Path to the dataset file
    """
    manager = DatasetManager()
    return manager.ensure_dataset()


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        datefmt="%H:%M:%S",
    )

    print("\n" + "=" * 70)
    print("  Phishing URL Detection - Dataset Manager")
    print("=" * 70 + "\n")

    try:
        dataset_path = setup_dataset()
        print(f"\n✅ Dataset ready at: {dataset_path}")
        print(f"   Size: {dataset_path.stat().st_size / (1024*1024):.1f} MB\n")
    except Exception as exc:
        print(f"\n❌ Error: {exc}\n")
        exit(1)
