"""
predict_url.py
==============
Offline URL phishing detection using trained models.

NO EXTERNAL API REQUIRED - Uses models directly from models_saved/

Usage:
  python predict_url.py "https://www.example.com"
  python predict_url.py "https://www.example.com" "https://www.google.com"
  python predict_url.py --interactive
  python predict_url.py --list-models
"""

import sys
import os
import json
import logging
import joblib
import numpy as np
from typing import List, Dict, Any
from pathlib import Path

# Import our modules
from feature_extraction import extract_features_from_url
from src.preprocessing.preprocessor import PhishingPreprocessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).parent.absolute()
MODELS_DIR = PROJECT_ROOT / "models_saved"
DEFAULT_MODEL = "xgboost"

# Global model cache
MODELS_CACHE = {}
PREPROCESSOR = None


# ============================================================================
# Model Loading
# ============================================================================

def load_model(model_name: str):
    """
    Load a trained model from disk.
    
    Parameters
    ----------
    model_name : str
        Name of the model (without .pkl extension)
        
    Returns
    -------
    Trained model object or None if not found
    """
    global MODELS_CACHE
    
    # Check cache first
    if model_name in MODELS_CACHE:
        return MODELS_CACHE[model_name]
    
    # Try to load from file
    model_file = MODELS_DIR / f"{model_name}.pkl"
    
    if not model_file.exists():
        logger.warning(f"Model file not found: {model_file}")
        return None
    
    try:
        logger.info(f"Loading model: {model_name}")
        model = joblib.load(str(model_file))
        MODELS_CACHE[model_name] = model
        return model
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        return None


def get_available_models() -> List[str]:
    """
    Get list of available trained models.
    
    Returns
    -------
    List[str]
        List of model names
    """
    if not MODELS_DIR.exists():
        return []
    
    models = []
    for model_file in MODELS_DIR.glob("*.pkl"):
        model_name = model_file.stem
        models.append(model_name)
    
    return sorted(models)


def init_preprocessor():
    """Initialize the preprocessor for feature scaling."""
    global PREPROCESSOR
    
    if PREPROCESSOR is not None:
        return PREPROCESSOR
    
    try:
        preprocessor_path = MODELS_DIR / "preprocessor.pkl"
        if preprocessor_path.exists():
            PREPROCESSOR = PhishingPreprocessor.load(str(preprocessor_path))
            logger.info("Preprocessor loaded from disk")
        else:
            logger.warning("preprocessor.pkl not found! Features will not be scaled. Re-run main.py to save it.")
            PREPROCESSOR = PhishingPreprocessor()
        return PREPROCESSOR
    except Exception as e:
        logger.error(f"Failed to initialize preprocessor: {e}")
        return None


# ============================================================================
# Prediction Functions
# ============================================================================

def predict_url(url: str, model_name: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Predict if a URL is phishing using offline models.
    
    Parameters
    ----------
    url : str
        URL to predict
    model_name : str
        Model to use for prediction
        
    Returns
    -------
    dict
        Prediction result with confidence
    """
    try:
        # Extract features from URL
        logger.info(f"Extracting features from URL: {url}")
        features = extract_features_from_url(url)
        features_array = np.array(features).reshape(1, -1)
        
        # Initialize preprocessor
        preprocessor = init_preprocessor()
        if preprocessor:
            try:
                features_array = preprocessor.transform(features_array)
            except Exception as e:
                logger.warning(f"Could not apply preprocessing: {e}")
        
        # Load model
        model = load_model(model_name)
        if model is None:
            return {
                "error": f"Model '{model_name}' not found",
                "available_models": get_available_models(),
                "url": url
            }
        
        # Make prediction
        prediction = model.predict(features_array)[0]
        
        # Get confidence/probability if available
        confidence = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features_array)[0]
            confidence = float(probs[1])  # Probability of phishing
        elif hasattr(model, "decision_function"):
            # For models without predict_proba
            score = model.decision_function(features_array)[0]
            confidence = float(1 / (1 + np.exp(-score)))  # Sigmoid
        
        return {
            "url": url,
            "prediction": int(prediction),
            "prediction_label": "Phishing" if prediction == 1 else "Legitimate",
            "confidence": confidence,
            "model": model_name,
            "source": "offline_model"
        }
    
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return {"error": str(e), "url": url}


def predict_batch(urls: List[str], model_name: str = DEFAULT_MODEL) -> List[Dict[str, Any]]:
    """
    Predict multiple URLs in batch.
    
    Parameters
    ----------
    urls : List[str]
        List of URLs to predict
    model_name : str
        Model to use
        
    Returns
    -------
    list
        List of prediction results
    """
    try:
        logger.info(f"Extracting features for {len(urls)} URLs...")
        all_features = [extract_features_from_url(url) for url in urls]
        features_array = np.array(all_features)
        
        # Apply preprocessing
        preprocessor = init_preprocessor()
        if preprocessor:
            try:
                features_array = preprocessor.transform(features_array)
            except Exception as e:
                logger.warning(f"Could not apply preprocessing: {e}")
        
        # Load model
        model = load_model(model_name)
        if model is None:
            return [{"error": f"Model '{model_name}' not found"}]
        
        # Make predictions
        predictions = model.predict(features_array)
        
        # Get probabilities if available
        probabilities = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features_array)
            probabilities = probs[:, 1].tolist()
        
        results = []
        for i, pred in enumerate(predictions):
            results.append({
                "id": i,
                "url": urls[i],
                "prediction": int(pred),
                "prediction_label": "Phishing" if pred == 1 else "Legitimate",
                "confidence": probabilities[i] if probabilities else None,
                "model": model_name,
            })
        
        return results
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}", exc_info=True)
        return [{"error": str(e)}]


# ============================================================================
# Display Functions
# ============================================================================

def print_result(result: Dict[str, Any]):
    """Pretty print a single prediction result."""
    if "error" in result:
        print(f"\n[ERROR] {result['error']}")
        if "available_models" in result:
            print(f"Available models: {result['available_models']}")
        return
    
    url = result.get("url", "Unknown")
    label = result.get("prediction_label", "Unknown")
    confidence = result.get("confidence")
    model = result.get("model", "Unknown")
    
    # Color coding
    if label == "Phishing":
        emoji = "[PHISHING]"
    else:
        emoji = "[LEGITIMATE]"
    
    print(f"\n{emoji} URL: {url}")
    print(f"    Result:     {label}")
    if confidence is not None:
        print(f"    Confidence: {confidence:.2%}")
    print(f"    Model:      {model}")


def print_batch_results(results: List[Dict[str, Any]]):
    """Pretty print batch prediction results."""
    print("\n" + "="*80)
    print("BATCH PREDICTION RESULTS")
    print("="*80)
    
    phishing_count = 0
    legitimate_count = 0
    error_count = 0
    
    for i, result in enumerate(results, 1):
        print(f"\n[{i}/{len(results)}]", end=" ")
        
        if "error" in result:
            print(f"ERROR: {result['error']}")
            error_count += 1
            continue
        
        url = result.get("url", "Unknown")
        label = result.get("prediction_label", "Unknown")
        confidence = result.get("confidence")
        
        # Emoji
        if label == "Phishing":
            phishing_count += 1
            emoji = "[PHISHING]"
        else:
            legitimate_count += 1
            emoji = "[LEGITIMATE]"
        
        print(f"{emoji} {url}")
        print(f"         -> {label}", end="")
        if confidence is not None:
            print(f" (confidence: {confidence:.2%})", end="")
        print()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    total = phishing_count + legitimate_count
    if total > 0:
        print(f"Total URLs:     {len(results)}")
        print(f"Phishing:       {phishing_count} ({phishing_count/total*100:.1f}%)")
        print(f"Legitimate:     {legitimate_count} ({legitimate_count/total*100:.1f}%)")
    if error_count > 0:
        print(f"Errors:         {error_count}")
    print("="*80)


def print_available_models():
    """Print available models."""
    models = get_available_models()
    
    print("\n" + "="*80)
    print("AVAILABLE MODELS")
    print("="*80)
    
    if not models:
        print("No models found in models_saved/")
        print("Run: python main.py --skip-eda")
        return
    
    for i, model in enumerate(models, 1):
        marker = " (DEFAULT)" if model == DEFAULT_MODEL else ""
        print(f"{i}. {model}{marker}")
    
    print("="*80 + "\n")


def interactive_mode():
    """Interactive URL prediction mode."""
    print("\n" + "="*80)
    print("PHISHING URL DETECTOR - INTERACTIVE MODE (OFFLINE)")
    print("="*80)
    print("\nEnter URLs to check (one per line).")
    print("Type 'quit' or 'exit' to stop.")
    print("Type 'models' to see available models.")
    print("Type 'model <name>' to change model (e.g., 'model logistic_regression').")
    print()
    
    current_model = DEFAULT_MODEL
    
    while True:
        try:
            user_input = input("\nEnter URL (or 'quit'): ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'models':
                print_available_models()
                continue
            
            if user_input.lower().startswith('model '):
                model_name = user_input[6:].strip()
                # Verify model exists
                if model_name in get_available_models():
                    current_model = model_name
                    print(f"Model changed to: {model_name}")
                else:
                    print(f"Model not found: {model_name}")
                    print(f"Available: {get_available_models()}")
                continue
            
            if not user_input:
                continue
            
            result = predict_url(user_input, current_model)
            print_result(result)
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        models = get_available_models()
        model_list = ", ".join(models) if models else "None (run: python main.py --skip-eda)"
        
        print(f"""
PHISHING URL DETECTION - OFFLINE MODEL PREDICTOR
(No API required - uses trained models directly)

USAGE: python predict_url.py [URLs...]

Examples:
  python predict_url.py "https://www.google.com"
  python predict_url.py "https://google.com" "https://github.com"
  python predict_url.py --interactive
  python predict_url.py --list-models
  
Options:
  --interactive, -i    Enter interactive mode
  --list-models        Show available models
  --model MODEL        Use specific model (default: {DEFAULT_MODEL})
  --help, -h          Show this help message

Default model: {DEFAULT_MODEL}
Available models: {model_list}
        """)
        return
    
    # Parse arguments
    urls = []
    model = DEFAULT_MODEL
    interactive = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['-i', '--interactive']:
            interactive = True
        elif arg == '--list-models':
            print_available_models()
            return
        elif arg in ['-h', '--help']:
            print(__doc__)
            return
        elif arg == '--model':
            if i + 1 < len(sys.argv):
                model = sys.argv[i + 1]
                i += 1
        elif not arg.startswith('-'):
            urls.append(arg)
        
        i += 1
    
    # Run appropriate mode
    if interactive:
        interactive_mode()
    elif urls:
        if len(urls) == 1:
            result = predict_url(urls[0], model)
            print_result(result)
        else:
            results = predict_batch(urls, model)
            print_batch_results(results)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
