import os
from src.preprocessing.data_loader import load_dataset, split_data, get_feature_names
from src.preprocessing.preprocessor import PhishingPreprocessor
from dataset_manager import DatasetManager

def main():
    dm = DatasetManager(auto_download=True)
    dataset_path = dm.ensure_dataset()
    df = load_dataset(str(dataset_path))
    feature_names = get_feature_names(df, "CLASS_LABEL")
    X_train_raw, _, _, y_train_raw, _, _ = split_data(df, "CLASS_LABEL")
    
    preprocessor = PhishingPreprocessor()
    preprocessor.fit_transform(X_train_raw, feature_names)
    preprocessor.save(os.path.join("models_saved", "preprocessor.pkl"))
    print("Saved preprocessor to models_saved/preprocessor.pkl")

if __name__ == "__main__":
    main()
