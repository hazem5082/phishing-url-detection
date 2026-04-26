"""
Model training module for phishing URL detection.
Implements 5 ML models with hyperparameter tuning and evaluation.
"""

import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb

from config import MODELS_DIR, REPORTS_DIR

# Setup logging
logger = logging.getLogger(__name__)


# ============================================================================
# Model Definitions and Hyperparameter Grids
# ============================================================================

MODELS_CONFIG = {
    'logistic_regression': {
        'model': LogisticRegression(random_state=42, max_iter=1000),
        'param_dist': {
            'C': [0.001, 0.01, 0.1, 1, 10, 100],
            'penalty': ['l2'],
            'class_weight': [None, 'balanced']
        }
    },
    'random_forest': {
        'model': RandomForestClassifier(random_state=42, n_jobs=-1),
        'param_dist': {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        }
    },
    'xgboost': {
        'model': xgb.XGBClassifier(random_state=42, eval_metric='logloss', n_jobs=-1),
        'param_dist': {
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0],
            'n_estimators': [100, 200, 300]
        }
    },
    'decision_tree': {
        'model': DecisionTreeClassifier(random_state=42),
        'param_dist': {
            'max_depth': [5, 10, 15, 20, None],
            'criterion': ['gini', 'entropy'],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
    },
    'mlp': {
        'model': MLPClassifier(random_state=42, max_iter=500),
        'param_dist': {
            'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
            'activation': ['relu', 'tanh'],
            'alpha': [0.0001, 0.001, 0.01],
            'learning_rate': ['constant', 'adaptive']
        }
    }
}


# ============================================================================
# Training Functions
# ============================================================================

def train_model(
    model: Any,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    param_dist: Dict[str, List[Any]],
    model_name: str,
    n_iter: int = 20,
    cv_folds: int = 5
) -> Tuple[Any, Dict[str, Any]]:
    """
    Train a single model with hyperparameter tuning.
    
    Args:
        model: The sklearn-compatible model
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        param_dist: Hyperparameter distribution for RandomizedSearchCV
        model_name: Name of the model for logging
        n_iter: Number of parameter settings sampled
        cv_folds: Number of cross-validation folds
        
    Returns:
        Tuple of (trained_model, results_dict)
    """
    logger.info(f"Training {model_name}...")
    
    # Setup cross-validation
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    
    # Hyperparameter tuning
    search = RandomizedSearchCV(
        model,
        param_distributions=param_dist,
        n_iter=n_iter,
        cv=cv,
        scoring='f1',
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    # Fit on training data
    search.fit(X_train, y_train)
    
    # Get best model
    best_model = search.best_estimator_
    
    # Evaluate on validation set
    y_val_pred = best_model.predict(X_val)
    val_accuracy = accuracy_score(y_val, y_val_pred)
    val_f1 = f1_score(y_val, y_val_pred)
    
    logger.info(f"{model_name} - Best params: {search.best_params_}")
    logger.info(f"{model_name} - Val Accuracy: {val_accuracy:.4f}, Val F1: {val_f1:.4f}")
    
    results = {
        'best_params': search.best_params_,
        'val_accuracy': val_accuracy,
        'val_f1': val_f1
    }
    
    return best_model, results


def evaluate_model(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    model_name: str
) -> Dict[str, Any]:
    """
    Evaluate a trained model on test set.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        model_name: Name of the model
        
    Returns:
        Dictionary of evaluation metrics
    """
    logger.info(f"Evaluating {model_name} on test set...")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # Classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    
    logger.info(f"{model_name} - Test Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
    
    results = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm,
        'classification_report': report
    }
    
    # Save confusion matrix visualization
    save_confusion_matrix(cm, model_name)
    
    return results


def save_confusion_matrix(cm: np.ndarray, model_name: str) -> None:
    """
    Save confusion matrix as a plot.
    
    Args:
        cm: Confusion matrix
        model_name: Name of the model
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            ax=ax,
            cbar_kws={'label': 'Count'}
        )
        ax.set_title(f'Confusion Matrix - {model_name}', fontweight='bold')
        ax.set_xlabel('Predicted Label')
        ax.set_ylabel('True Label')
        ax.set_xticklabels(['Legitimate', 'Phishing'])
        ax.set_yticklabels(['Legitimate', 'Phishing'])
        
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / f'confusion_matrix_{model_name}.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved confusion matrix for {model_name}")
    except Exception as e:
        logger.warning(f"Could not save confusion matrix plot: {e}")


def save_model(model: Any, model_name: str) -> None:
    """
    Save a trained model to disk.
    
    Args:
        model: Trained model
        model_name: Name of the model
    """
    model_path = MODELS_DIR / f'{model_name}.pkl'
    joblib.dump(model, model_path)
    logger.info(f"Saved model to {model_path}")


# ============================================================================
# Main Training Pipeline
# ============================================================================

def run_all_models(
    X_train: np.ndarray,
    X_val: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_val: np.ndarray,
    y_test: np.ndarray,
    n_iter: int = 20,
    cv_folds: int = 5
) -> List[Dict[str, Any]]:
    """
    Train and evaluate all models.
    
    Args:
        X_train: Training features
        X_val: Validation features
        X_test: Test features
        y_train: Training labels
        y_val: Validation labels
        y_test: Test labels
        n_iter: Number of parameter settings for RandomizedSearchCV
        cv_folds: Number of cross-validation folds
        
    Returns:
        List of result dictionaries for each model
    """
    logger.info("="*60)
    logger.info("Starting model training pipeline")
    logger.info("="*60)
    
    results = []
    
    for model_name, config in MODELS_CONFIG.items():
        try:
            # Train model
            trained_model, train_results = train_model(
                config['model'],
                X_train, y_train,
                X_val, y_val,
                config['param_dist'],
                model_name,
                n_iter,
                cv_folds
            )
            
            # Evaluate on test set
            test_results = evaluate_model(
                trained_model,
                X_test,
                y_test,
                model_name
            )
            
            # Save model
            save_model(trained_model, model_name)
            
            # Combine results
            combined_results = {
                'name': model_name,
                **train_results,
                **test_results
            }
            results.append(combined_results)
            
        except Exception as e:
            logger.error(f"Error training {model_name}: {e}", exc_info=True)
            results.append({
                'name': model_name,
                'error': str(e)
            })
    
    # Print summary
    logger.info("="*60)
    logger.info("Model Training Summary")
    logger.info("="*60)
    for result in results:
        if 'error' not in result:
            logger.info(
                f"{result['name']}: "
                f"Accuracy={result['accuracy']:.4f}, "
                f"F1={result['f1']:.4f}"
            )
        else:
            logger.error(f"{result['name']}: {result['error']}")
    
    return results


# ============================================================================
# Helper Functions
# ============================================================================

def load_model(model_name: str) -> Any:
    """
    Load a trained model from disk.
    
    Args:
        model_name: Name of the model (without .pkl extension)
        
    Returns:
        Loaded model
    """
    model_path = MODELS_DIR / f'{model_name}.pkl'
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    model = joblib.load(model_path)
    logger.info(f"Loaded model from {model_path}")
    return model


def list_available_models() -> List[str]:
    """
    List all available trained models.
    
    Returns:
        List of model names
    """
    model_files = list(MODELS_DIR.glob('*.pkl'))
    model_names = [f.stem for f in model_files if f.stem != 'preprocessor']
    return sorted(model_names)
