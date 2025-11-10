import pickle
import json
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any
from src.core.config import get_settings

settings = get_settings()


class ModelLoader:
    _instance = None
    _model = None
    _scaler = None
    _metadata = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_artifacts()
        return cls._instance
    
    def _load_artifacts(self):
        try:
            model_path = Path(settings.MODEL_PATH)
            with open(model_path, 'rb') as f:
                self._model = pickle.load(f)
            
            scaler_path = Path(settings.SCALER_PATH)
            with open(scaler_path, 'rb') as f:
                self._scaler = pickle.load(f)
            
            metadata_path = Path(settings.METADATA_PATH)
            with open(metadata_path, 'r') as f:
                self._metadata = json.load(f)
            
            print(f"Model loaded successfully")
            print(f"   Model: {self._metadata['model_type']}")
            print(f"   Threshold: {self._metadata['optimal_threshold']:.4f}")
            print(f"   Precision: {self._metadata['test_metrics']['precision']:.2%}")
            print(f"   Recall: {self._metadata['test_metrics']['recall']:.2%}")
            
        except Exception as e:
            print(f"Error loading model artifacts: {e}")
            raise
    
    def get_model(self):
        return self._model
    
    def get_scaler(self):
        return self._scaler
    
    def get_metadata(self) -> Dict[str, Any]:
        return self._metadata
    
    def get_threshold(self) -> float:
        return self._metadata['optimal_threshold']
    
    def predict(self, features: np.ndarray) -> Tuple[int, float, str]:
        anomaly_score = self._model.decision_function(features)[0]
        threshold = self.get_threshold()
        prediction = 1 if anomaly_score < threshold else 0
        fraud_probability = max(0, min(1, (threshold - anomaly_score) / (threshold + 0.1)))
        
        if fraud_probability >= 0.7:
            risk_level = "HIGH"
        elif fraud_probability >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return prediction, fraud_probability, risk_level


model_loader = ModelLoader()
