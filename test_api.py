"""
test_api.py
===========
Comprehensive testing utility for the Phishing URL Detection REST API.

This script provides multiple ways to test the API:
1. Health check
2. Single predictions with sample data
3. Batch predictions
4. Model comparison

Note: The model expects 48 pre-extracted features (not raw URLs).
The Kaggle dataset provides these features already extracted.
"""

import json
import requests
import numpy as np
from typing import List, Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:5000"

# ============================================================================
# Sample Feature Vectors
# ============================================================================
# These are 48-feature vectors representing phishing and legitimate URLs
# from the Kaggle dataset

# Example 1: Phishing URL features (typical)
SAMPLE_PHISHING = [
    -0.9, -0.8, 0.2, 0.1, 0.3, 0.4, 0.5, 0.6,
    0.1, -0.5, 0.2, 0.3, 0.4, -0.7, 0.8, 0.9,
    0.2, 0.3, 0.4, -0.2, 0.1, 0.2, 0.3, 0.4,
    0.5, 0.6, -0.3, 0.2, 0.1, 0.0, 0.1, 0.2,
    0.3, 0.4, 0.5, -0.1, 0.2, 0.3, 0.4, 0.5,
    0.6, 0.7, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7
]

# Example 2: Legitimate URL features (typical)
SAMPLE_LEGITIMATE = [
    0.9, 0.8, -0.2, -0.1, -0.3, 0.4, 0.5, 0.6,
    -0.1, 0.5, -0.2, -0.3, 0.4, 0.7, -0.8, -0.9,
    -0.2, 0.3, -0.4, 0.2, -0.1, -0.2, 0.3, -0.4,
    0.5, -0.6, 0.3, -0.2, -0.1, 0.0, -0.1, -0.2,
    0.3, -0.4, 0.5, 0.1, -0.2, 0.3, -0.4, 0.5,
    -0.6, 0.7, -0.2, 0.3, -0.4, 0.5, -0.6, -0.7
]

# Example 3: Random features for testing
SAMPLE_RANDOM = np.random.randn(48).tolist()


# ============================================================================
# Test Functions
# ============================================================================

def test_health_check():
    """Test the /health endpoint."""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure it's running:")
        print("  python startup.py")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_list_models():
    """Test the /models endpoint."""
    print("\n" + "="*70)
    print("TEST 2: List Available Models")
    print("="*70)
    
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Available Models: {data.get('models', [])}")
        print(f"Count: {data.get('count', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_single_prediction(features: List[float], model_name: str = "XGBoost"):
    """
    Test single prediction endpoint.
    
    Parameters
    ----------
    features : List[float]
        Array of 48 features
    model_name : str
        Name of model to use for prediction
    """
    print("\n" + "="*70)
    print(f"TEST 3: Single Prediction ({model_name})")
    print("="*70)
    
    if len(features) != 48:
        print(f"ERROR: Expected 48 features, got {len(features)}")
        return False
    
    try:
        payload = {
            "features": features,
            "model": model_name
        }
        
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_batch_predictions(feature_list: List[List[float]], model_name: str = "XGBoost"):
    """
    Test batch prediction endpoint.
    
    Parameters
    ----------
    feature_list : List[List[float]]
        List of feature arrays (each with 48 features)
    model_name : str
        Name of model to use
    """
    print("\n" + "="*70)
    print(f"TEST 4: Batch Predictions ({len(feature_list)} URLs)")
    print("="*70)
    
    try:
        payload = {
            "features": feature_list,
            "model": model_name
        }
        
        response = requests.post(
            f"{API_BASE_URL}/predict-batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Predictions: {data.get('count', 0)} URLs processed")
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_all_models(features: List[float]):
    """
    Test prediction with all available models.
    
    Parameters
    ----------
    features : List[float]
        Array of 48 features
    """
    print("\n" + "="*70)
    print("TEST 5: Model Comparison (All Models)")
    print("="*70)
    
    try:
        # Get list of models
        response = requests.get(f"{API_BASE_URL}/models")
        models = response.json().get("models", [])
        
        results = []
        for model in models:
            payload = {"features": features, "model": model}
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "model": model,
                    "prediction": data.get("prediction"),
                    "confidence": data.get("confidence"),
                })
        
        # Display comparison
        print("\nModel Comparison Results:")
        print("-" * 70)
        for result in results:
            pred_label = "Phishing" if result["prediction"] == 1 else "Legitimate"
            conf = result.get("confidence") or "N/A"
            print(f"{result['model']:20} -> {pred_label:12} (confidence: {conf})")
        
        return len(results) > 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_error_handling():
    """Test API error handling."""
    print("\n" + "="*70)
    print("TEST 6: Error Handling")
    print("="*70)
    
    # Test 1: Invalid feature count
    print("\n[Test 6a] Invalid feature count")
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"features": [0.1] * 10}  # Only 10 instead of 48
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 2: Missing features field
    print("\n[Test 6b] Missing features field")
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"model": "XGBoost"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 3: Invalid model name
    print("\n[Test 6c] Invalid model name")
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"features": SAMPLE_PHISHING, "model": "InvalidModel"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"ERROR: {e}")


def run_full_test_suite():
    """Run all tests."""
    print("\n" * 2)
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  PHISHING URL DETECTION - API TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "Health Check": test_health_check(),
        "List Models": test_list_models(),
        "Phishing Prediction": test_single_prediction(SAMPLE_PHISHING),
        "Legitimate Prediction": test_single_prediction(SAMPLE_LEGITIMATE),
        "Batch Predictions": test_batch_predictions(
            [SAMPLE_PHISHING, SAMPLE_LEGITIMATE, SAMPLE_RANDOM]
        ),
        "Model Comparison": test_all_models(SAMPLE_PHISHING),
    }
    
    test_error_handling()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:30} {status}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70 + "\n")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("""
IMPORTANT: Before running tests, make sure the API is running:
  
  Option 1 (Recommended): python startup.py
  Option 2:               python app.py
  Option 3 (Docker):      docker-compose up

The API should be available at http://localhost:5000

Note: The model expects 48 numerical features, not raw URLs.
The features are pre-extracted from URLs using URL analysis techniques.
""")
    
    input("Press Enter to start tests...\n")
    
    run_full_test_suite()
