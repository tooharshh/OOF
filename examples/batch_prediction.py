"""
Example: Batch Transaction Prediction

This script demonstrates how to make batch fraud prediction requests.
"""
import requests
import json
from datetime import datetime
import random


# Configuration
API_URL = "http://localhost:8000"
API_KEY = "dev-key-12345"


def generate_sample_transaction():
    """
    Generate a random sample transaction for testing
    """
    return {
        "V1": random.uniform(-3, 3),
        "V2": random.uniform(-3, 3),
        "V3": random.uniform(-3, 3),
        "V4": random.uniform(-3, 3),
        "V5": random.uniform(-3, 3),
        "V6": random.uniform(-3, 3),
        "V7": random.uniform(-3, 3),
        "V8": random.uniform(-3, 3),
        "V9": random.uniform(-3, 3),
        "V10": random.uniform(-3, 3),
        "V11": random.uniform(-3, 3),
        "V12": random.uniform(-3, 3),
        "V13": random.uniform(-3, 3),
        "V14": random.uniform(-3, 3),
        "V15": random.uniform(-3, 3),
        "V16": random.uniform(-3, 3),
        "V17": random.uniform(-3, 3),
        "V18": random.uniform(-3, 3),
        "V19": random.uniform(-3, 3),
        "V20": random.uniform(-3, 3),
        "V21": random.uniform(-3, 3),
        "V22": random.uniform(-3, 3),
        "V23": random.uniform(-3, 3),
        "V24": random.uniform(-3, 3),
        "V25": random.uniform(-3, 3),
        "V26": random.uniform(-3, 3),
        "V27": random.uniform(-3, 3),
        "V28": random.uniform(-3, 3),
        "Time": random.uniform(0, 172800),
        "Amount": random.uniform(0.01, 1000)
    }


def predict_batch_transactions(num_transactions=10):
    """
    Make a batch prediction request
    """
    # Generate sample transactions
    transactions = [generate_sample_transaction() for _ in range(num_transactions)]
    transaction_ids = [
        f"BATCH-{datetime.now().strftime('%Y%m%d')}-{i:04d}"
        for i in range(num_transactions)
    ]
    
    batch_request = {
        "transactions": transactions,
        "transaction_ids": transaction_ids
    }
    
    # Make API request
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Making batch prediction request for {num_transactions} transactions...")
    
    response = requests.post(
        f"{API_URL}/api/v1/predict/batch",
        json=batch_request,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Batch prediction successful!")
        print(f"\n{'='*60}")
        print(f"Total Transactions: {result['total_transactions']}")
        print(f"Fraud Count: {result['fraud_count']}")
        print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
        print(f"Avg Time per Transaction: {result['processing_time_ms']/result['total_transactions']:.2f}ms")
        print(f"{'='*60}\n")
        
        # Show details of first 5 predictions
        print("📊 Sample Predictions (first 5):")
        for i, pred in enumerate(result['predictions'][:5]):
            print(f"\n  Transaction {i+1}: {pred['transaction_id']}")
            print(f"    Fraud: {'🚨 YES' if pred['is_fraud'] else '✅ NO'}")
            print(f"    Probability: {pred['fraud_probability']:.4f} ({pred['fraud_probability']*100:.2f}%)")
            print(f"    Risk Level: {pred['risk_level']}")
        
        # Summary statistics
        fraud_probs = [p['fraud_probability'] for p in result['predictions']]
        avg_prob = sum(fraud_probs) / len(fraud_probs)
        max_prob = max(fraud_probs)
        
        print(f"\n{'='*60}")
        print("📈 Summary Statistics:")
        print(f"  Average Fraud Probability: {avg_prob:.4f} ({avg_prob*100:.2f}%)")
        print(f"  Maximum Fraud Probability: {max_prob:.4f} ({max_prob*100:.2f}%)")
        print(f"  Fraud Rate: {result['fraud_count']}/{result['total_transactions']} ({result['fraud_count']/result['total_transactions']*100:.2f}%)")
        print(f"{'='*60}\n")
        
        return result
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("FRAUD DETECTION API - BATCH PREDICTION EXAMPLE")
    print("="*60 + "\n")
    
    # Check API health first
    print("🏥 Checking API health...")
    health_response = requests.get(f"{API_URL}/api/v1/health")
    if health_response.status_code == 200:
        health = health_response.json()
        print(f"✅ API Status: {health['status']}")
        print(f"🤖 Model Loaded: {health['model_loaded']}\n")
    else:
        print("❌ API is not available!")
        exit(1)
    
    # Test with different batch sizes
    batch_sizes = [10, 50, 100]
    
    for size in batch_sizes:
        print(f"\n{'='*60}")
        print(f"Testing with batch size: {size}")
        print(f"{'='*60}")
        result = predict_batch_transactions(size)
        if not result:
            break
    
    print("\n✨ Batch prediction examples completed!")
