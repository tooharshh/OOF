# Example API Usage Scripts

This directory contains example scripts for interacting with the Fraud Detection API.

## Available Examples

### 1. Single Prediction
```python
python examples/single_prediction.py
```

### 2. Batch Prediction
```python
python examples/batch_prediction.py
```

### 3. Load Testing
```python
python examples/load_test.py
```

## Requirements

```bash
pip install requests
```

## Configuration

Set your API key:
```python
API_KEY = "dev-key-12345"  # Change to your actual API key
```

Set API URL:
```python
API_URL = "http://localhost:8000"  # Change if deployed elsewhere
```
