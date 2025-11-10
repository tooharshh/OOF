from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class FeedbackCreate(BaseModel):
    prediction_id: UUID
    actual_label: bool
    feedback_source: str = Field(..., max_length=50)
    notes: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: UUID
    prediction_id: UUID
    actual_label: bool
    feedback_source: str
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionDetail(BaseModel):
    id: UUID
    transaction_id: str
    prediction: bool
    fraud_probability: float
    risk_level: str
    anomaly_score: float
    threshold_used: float
    model_version: str
    created_at: datetime
    feedback: Optional[FeedbackResponse] = None
    
    class Config:
        from_attributes = True
        protected_namespaces = ()  # Disable Pydantic protected namespace warning
