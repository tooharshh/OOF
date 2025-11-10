import pytest
import numpy as np
from src.core.model_loader import model_loader
from src.core.config import get_settings

settings = get_settings()

def test_model_loading():
    model = model_loader.get_model()
    scaler = model_loader.get_scaler()
    metadata = model_loader.get_metadata()
    
    assert model is not None
    assert scaler is not None
    assert metadata is not None

def test_predict_with_valid_data():
    features = np.random.randn(1, 30)
    
    prediction, fraud_probability, risk_level = model_loader.predict(features)
    
    assert prediction in [0, 1]
    assert 0 <= fraud_probability <= 1
    assert risk_level in ["LOW", "MEDIUM", "HIGH"]

def test_predict_with_different_thresholds():
    features = np.random.randn(1, 30)
    
    prediction, fraud_prob, risk_level = model_loader.predict(features)
    
    assert isinstance(prediction, (int, np.integer))
    assert isinstance(fraud_prob, (float, np.floating, int, np.integer))
    assert 0 <= fraud_prob <= 1

def test_risk_level_calculation():
    features = np.random.randn(1, 30)
    
    prediction, fraud_probability, risk_level = model_loader.predict(features)
    
    if fraud_probability < 0.3:
        assert risk_level == "LOW"
    elif fraud_probability < 0.7:
        assert risk_level == "MEDIUM"
    else:
        assert risk_level == "HIGH"

def test_model_consistency():
    features = np.random.randn(1, 30)
    
    pred1, prob1, risk1 = model_loader.predict(features)
    pred2, prob2, risk2 = model_loader.predict(features)
    
    assert pred1 == pred2
    assert abs(prob1 - prob2) < 0.001

def test_batch_predictions():
    features = np.random.randn(10, 30)
    
    results = []
    for i in range(10):
        prediction, fraud_prob, risk_level = model_loader.predict(features[i:i+1])
        results.append((prediction, fraud_prob, risk_level))
    
    assert len(results) == 10
    for prediction, fraud_prob, risk_level in results:
        assert prediction in [0, 1]
        assert 0 <= fraud_prob <= 1
        assert risk_level in ["LOW", "MEDIUM", "HIGH"]
