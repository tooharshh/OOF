"""
Example: Single Transaction Prediction

This script demonstrates how to make a single fraud prediction request.
"""
import requests
import json
from datetime import datetime


# Configuration
API_URL = "http://localhost:8000"
API_KEY = "dev-key-12345"


def predict_single_transaction():
    """
    Make a single transaction prediction
    """
    # Sample transaction (from Credit Card Fraud dataset)
    transaction = {
        "transaction_id": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "transaction": {
            "V1": -1.3598071336738,
            "V2": -0.0727811733098497,
            "V3": 2.53634673796914,
            "V4": 1.37815522427443,
            "V5": -0.338320769942518,
            "V6": 0.462387777762292,
            "V7": 0.239598554061257,
            "V8": 0.0986979012610507,
            "V9": 0.363786969611213,
            "V10": 0.0907941719789316,
            "V11": -0.551599533260813,
            "V12": -0.617800855762348,
            "V13": -0.991389847235408,
            "V14": -0.311169353699879,
            "V15": 1.46817697209427,
            "V16": -0.470400525259478,
            "V17": 0.207971241929242,
            "V18": 0.0257905801985591,
            "V19": 0.403992960255733,
            "V20": 0.251412098239705,
            "V21": -0.018306777944153,
            "V22": 0.277837575558899,
            "V23": -0.110473910188767,
            "V24": 0.0669280749146731,
            "V25": 0.128539358273528,
            "V26": -0.189114843888824,
            "V27": 0.133558376740387,
            "V28": -0.0210530534538215,
            "Time": 406.0,
            "Amount": 149.62
        }
    }
    
    # Make API request
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("🔍 Making fraud prediction request...")
    print(f"Transaction ID: {transaction['transaction_id']}")
    print(f"Amount: ${transaction['transaction']['Amount']:.2f}")
    
    response = requests.post(
        f"{API_URL}/api/v1/predict",
        json=transaction,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Prediction successful!")
        print(f"\n{'='*60}")
        print(f"Transaction ID: {result['transaction_id']}")
        print(f"Is Fraud: {'🚨 YES' if result['is_fraud'] else '✅ NO'}")
        print(f"Fraud Probability: {result['fraud_probability']:.4f} ({result['fraud_probability']*100:.2f}%)")
        print(f"Anomaly Score: {result['anomaly_score']:.4f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"{'='*60}\n")
        
        return result
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("FRAUD DETECTION API - SINGLE PREDICTION EXAMPLE")
    print("="*60 + "\n")
    
    # Check API health first
    print("🏥 Checking API health...")
    health_response = requests.get(f"{API_URL}/api/v1/health")
    if health_response.status_code == 200:
        health = health_response.json()
        print(f"✅ API Status: {health['status']}")
        print(f"📦 Version: {health['version']}")
        print(f"🤖 Model Loaded: {health['model_loaded']}\n")
    else:
        print("❌ API is not available!")
        exit(1)
    
    # Make prediction
    result = predict_single_transaction()
    
    if result:
        print("✨ Example completed successfully!")
    else:
        print("❌ Example failed!")
