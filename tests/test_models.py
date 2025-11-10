import numpy as np
from src.core.model_loader import model_loader

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
