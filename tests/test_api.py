import requests

API_URL = "http://localhost:8000"
API_KEY = "dev-key-12345"

def test_root_endpoint():
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Fraud Detection API"
    assert "version" in data

def test_health_check():
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True

def test_predict_without_api_key():
    transaction = {
        "transaction_id": "TEST-001",
        "transaction": {
            "V1": 0.0, "V2": 0.0, "V3": 0.0, "V4": 0.0,
            "V5": 0.0, "V6": 0.0, "V7": 0.0, "V8": 0.0,
            "V9": 0.0, "V10": 0.0, "V11": 0.0, "V12": 0.0,
            "V13": 0.0, "V14": 0.0, "V15": 0.0, "V16": 0.0,
            "V17": 0.0, "V18": 0.0, "V19": 0.0, "V20": 0.0,
            "V21": 0.0, "V22": 0.0, "V23": 0.0, "V24": 0.0,
            "V25": 0.0, "V26": 0.0, "V27": 0.0, "V28": 0.0,
            "Time": 0.0,
            "Amount": 100.0
        }
    }
    response = requests.post(f"{API_URL}/api/v1/predict", json=transaction)
    assert response.status_code == 403