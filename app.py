"""
app.py
======
Production Flask REST API for the phishing URL detection system.

Endpoints:
  GET  /health              - Health check
  POST /predict             - Single URL prediction
  POST /predict-batch       - Batch prediction
  GET  /models              - List available models
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import numpy as np
from flask import Flask, request, jsonify

from config import (
    API_HOST,
    API_PORT,
    API_DEBUG,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    MODELS_DIR,
)
from src.preprocessing.preprocessor import PhishingPreprocessor

# ============================================================================
# Setup
# ============================================================================
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Global state for loaded models
MODELS = {}
PREPROCESSOR = None


# ============================================================================
# Startup & Shutdown
# ============================================================================
def load_models():
    """Load all trained models from disk."""
    global MODELS
    models_dir = Path(MODELS_DIR)
    
    if not models_dir.exists():
        logger.warning(f"Models directory not found: {models_dir}")
        return {}
    
    model_files = list(models_dir.glob("*.pkl"))
    if not model_files:
        logger.warning(f"No model files found in: {models_dir}")
        return {}
    
    logger.info(f"Found {len(model_files)} model file(s)")
    
    import joblib
    for model_file in model_files:
        try:
            model_name = model_file.stem
            model = joblib.load(str(model_file))
            MODELS[model_name] = model
            logger.info(f"✓ Loaded model: {model_name}")
        except Exception as exc:
            logger.error(f"✗ Failed to load {model_file.name}: {exc}")
    
    return MODELS


def load_preprocessor():
    """Initialize preprocessor for data transformation."""
    global PREPROCESSOR
    try:
        preprocessor_path = Path(MODELS_DIR) / "preprocessor.pkl"
        if preprocessor_path.exists():
            PREPROCESSOR = PhishingPreprocessor.load(str(preprocessor_path))
            logger.info("✓ Preprocessor loaded from disk")
        else:
            logger.warning("⚠ preprocessor.pkl not found! Features will not be scaled. Re-run main.py to save it.")
            PREPROCESSOR = PhishingPreprocessor()
        return PREPROCESSOR
    except Exception as exc:
        logger.error(f"✗ Failed to initialize preprocessor: {exc}")
        raise


@app.before_request
def startup():
    """Initialize on first request."""
    if not MODELS:
        logger.info("Initializing application...")
        load_preprocessor()
        load_models()
        if not MODELS:
            logger.warning("⚠ No models loaded. Predictions will fail.")
        logger.info("✓ Application ready")


# ============================================================================
# Health & Status Endpoints
# ============================================================================
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok" if MODELS else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": len(MODELS),
        "available_models": list(MODELS.keys()),
    }), 200 if MODELS else 503


@app.get("/models")
def list_models():
    """List available models."""
    return jsonify({
        "models": list(MODELS.keys()),
        "count": len(MODELS),
        "timestamp": datetime.utcnow().isoformat(),
    })


# ============================================================================
# Prediction Endpoints
# ============================================================================
@app.post("/predict")
def predict_single():
    """
    Predict phishing probability for a single URL.

    Request body:
    {
        "features": [float, ...],  # Array of 48 features
        "model": "LogisticRegression"  # Optional model selection
    }

    Returns:
    {
        "prediction": 0,  # 0=Legitimate, 1=Phishing
        "probability": 0.92,
        "model": "XGBoost",
        "timestamp": "2026-04-24T17:59:00"
    }
    """
    try:
        if not MODELS:
            return jsonify({"error": "No models available"}), 503

        data = request.get_json()
        if not data or "features" not in data:
            return jsonify({"error": "Missing 'features' field"}), 400

        features = np.array(data["features"]).reshape(1, -1)
        if features.shape[1] != 48:
            return jsonify({
                "error": f"Expected 48 features, got {features.shape[1]}"
            }), 400

        # Select model (default to first available)
        model_name = data.get("model", list(MODELS.keys())[0])
        if model_name not in MODELS:
            return jsonify({
                "error": f"Model '{model_name}' not found. Available: {list(MODELS.keys())}"
            }), 400

        model = MODELS[model_name]

        # Transform features using preprocessor
        if PREPROCESSOR:
            features = PREPROCESSOR.transform(features)

        # Make prediction
        prediction = model.predict(features)[0]
        
        # Get probability if available
        probability = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features)[0]
            probability = float(probs[1])  # Probability of phishing
        elif hasattr(model, "decision_function"):
            # For models without predict_proba
            prob_score = model.decision_function(features)[0]
            probability = float(1 / (1 + np.exp(-prob_score)))  # Sigmoid

        return jsonify({
            "prediction": int(prediction),
            "prediction_label": "Phishing" if prediction == 1 else "Legitimate",
            "confidence": probability if probability is not None else None,
            "model": model_name,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as exc:
        logger.error(f"Prediction error: {exc}", exc_info=True)
        return jsonify({"error": f"Prediction failed: {str(exc)}"}), 500


@app.post("/predict-batch")
def predict_batch():
    """
    Predict phishing for multiple URLs.

    Request body:
    {
        "features": [[float, ...], ...],  # Array of feature arrays
        "model": "XGBoost"  # Optional
    }

    Returns array of predictions.
    """
    try:
        if not MODELS:
            return jsonify({"error": "No models available"}), 503

        data = request.get_json()
        if not data or "features" not in data:
            return jsonify({"error": "Missing 'features' field"}), 400

        features = np.array(data["features"])
        if features.shape[1] != 48:
            return jsonify({
                "error": f"Expected 48 features per sample, got {features.shape[1]}"
            }), 400

        # Select model
        model_name = data.get("model", list(MODELS.keys())[0])
        if model_name not in MODELS:
            return jsonify({
                "error": f"Model '{model_name}' not found"
            }), 400

        model = MODELS[model_name]

        # Transform features
        if PREPROCESSOR:
            features = PREPROCESSOR.transform(features)

        # Make predictions
        predictions = model.predict(features)

        # Get probabilities if available
        probabilities = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features)
            probabilities = probs[:, 1].tolist()  # Phishing probability

        results = []
        for i, pred in enumerate(predictions):
            results.append({
                "id": i,
                "prediction": int(pred),
                "prediction_label": "Phishing" if pred == 1 else "Legitimate",
                "confidence": probabilities[i] if probabilities else None,
            })

        return jsonify({
            "predictions": results,
            "count": len(results),
            "model": model_name,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as exc:
        logger.error(f"Batch prediction error: {exc}", exc_info=True)
        return jsonify({"error": f"Batch prediction failed: {str(exc)}"}), 500


# ============================================================================
# Error Handlers
# ============================================================================
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# Main
# ============================================================================
if __name__ == "__main__":
    logger.info(f"Starting Flask API on {API_HOST}:{API_PORT}")
    logger.info(f"Debug mode: {API_DEBUG}")
    logger.info(f"Environment: production")
    
    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=API_DEBUG,
        use_reloader=False,
    )
