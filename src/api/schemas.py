from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class TransactionFeatures(BaseModel):
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Time: float = Field(..., description="Time in seconds since first transaction")
    Amount: float = Field(..., ge=0, description="Transaction amount")
    
    class Config:
        json_schema_extra = {
            "example": {
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
                "Time": 0.0,
                "Amount": 149.62
            }
        }


class PredictionRequest(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    transaction: TransactionFeatures
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-2024-001",
                "transaction": TransactionFeatures.Config.json_schema_extra["example"]
            }
        }


class PredictionResponse(BaseModel):
    transaction_id: str
    prediction: int = Field(..., description="0 = Legitimate, 1 = Fraud")
    fraud_probability: float = Field(..., ge=0, le=1, description="Probability of fraud (0-1)")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH")
    anomaly_score: float
    threshold: float
    timestamp: datetime
    model_version: str
    
    class Config:
        protected_namespaces = ()
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-2024-001",
                "prediction": 0,
                "fraud_probability": 0.15,
                "risk_level": "LOW",
                "anomaly_score": 0.2571,
                "threshold": 0.1284,
                "timestamp": "2024-11-10T10:30:00",
                "model_version": "1.0.0"
            }
        }


class BatchPredictionRequest(BaseModel):
    transactions: list[PredictionRequest] = Field(..., max_length=100)


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    total_processed: int
    fraud_detected: int
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    model_type: Optional[str] = None
    model_metrics: Optional[dict] = None
    
    class Config:
        protected_namespaces = ()


# Simplified Schema for User-Friendly Input
class SimpleTransactionInput(BaseModel):
    """
    Simplified transaction input - users only need to provide basic info.
    The API will use default/average values for the PCA features (V1-V28).
    """
    amount: float = Field(..., ge=0, description="Transaction amount in dollars", example=149.62)
    time_of_day: Optional[str] = Field(None, description="Time of transaction: morning, afternoon, evening, night", example="morning")
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 149.62,
                "time_of_day": "morning"
            }
        }


class SimpleTransactionRequest(BaseModel):
    """Simple prediction request - easy for non-technical users"""
    transaction_id: str = Field(..., description="Unique transaction identifier", example="TXN-2025-001")
    transaction: SimpleTransactionInput
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-2025-001",
                "transaction": {
                    "amount": 149.62,
                    "time_of_day": "morning"
                }
            }
        }

