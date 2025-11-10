from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Prediction, Feedback, APIUsage, ModelVersion

async def create_prediction(
    db: AsyncSession,
    transaction_id: str,
    prediction: bool,
    fraud_probability: float,
    risk_level: str,
    anomaly_score: float,
    threshold: float,
    model_version: str,
    features: dict
) -> Prediction:
    db_prediction = Prediction(
        transaction_id=transaction_id,
        prediction=prediction,
        fraud_probability=fraud_probability,
        risk_level=risk_level,
        anomaly_score=anomaly_score,
        threshold_used=threshold,
        model_version=model_version,
        features=features
    )
    db.add(db_prediction)
    await db.commit()
    await db.refresh(db_prediction)
    return db_prediction

async def get_prediction(db: AsyncSession, prediction_id: UUID) -> Optional[Prediction]:
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    return result.scalar_one_or_none()

async def get_prediction_by_transaction_id(
    db: AsyncSession, 
    transaction_id: str
) -> Optional[Prediction]:
    result = await db.execute(
        select(Prediction).where(Prediction.transaction_id == transaction_id)
    )
    return result.scalar_one_or_none()

async def get_predictions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    fraud_only: bool = False
) -> List[Prediction]:
    query = select(Prediction).order_by(desc(Prediction.created_at))
    
    if fraud_only:
        query = query.where(Prediction.prediction == True)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_feedback(
    db: AsyncSession,
    prediction_id: UUID,
    actual_label: bool,
    feedback_source: str,
    notes: Optional[str] = None
) -> Feedback:
    db_feedback = Feedback(
        prediction_id=prediction_id,
        actual_label=actual_label,
        feedback_source=feedback_source,
        notes=notes
    )
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    return db_feedback

async def log_api_usage(
    db: AsyncSession,
    api_key: str,
    endpoint: str,
    method: str,
    status_code: int,
    response_time_ms: float
):
    db_usage = APIUsage(
        api_key=api_key,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time_ms=response_time_ms
    )
    db.add(db_usage)
    await db.commit()

async def create_model_version(
    db: AsyncSession,
    version: str,
    threshold: float,
    metrics: dict,
    is_active: bool = False
) -> ModelVersion:
    if is_active:
        await db.execute(
            ModelVersion.__table__.update().values(is_active=False)
        )
    
    db_model = ModelVersion(
        version=version,
        threshold=threshold,
        metrics=metrics,
        is_active=is_active
    )
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)
    return db_model

async def get_active_model_version(db: AsyncSession) -> Optional[ModelVersion]:
    result = await db.execute(
        select(ModelVersion).where(ModelVersion.is_active == True)
    )
    return result.scalar_one_or_none()
