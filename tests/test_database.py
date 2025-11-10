import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import crud
from src.db.models import Prediction, Feedback, APIUsage, ModelVersion

@pytest.mark.asyncio
async def test_create_prediction(test_db: AsyncSession):
    prediction_data = {
        "transaction_id": "TEST-DB-001",
        "prediction": True,
        "fraud_probability": 0.85,
        "risk_level": "HIGH",
        "anomaly_score": 0.92,
        "threshold_used": 0.5,
        "model_version": "v1.0",
        "features": {"V1": 1.0, "V2": 2.0}
    }
    
    prediction = await crud.create_prediction(test_db, **prediction_data)
    
    assert prediction.id is not None
    assert prediction.transaction_id == "TEST-DB-001"
    assert prediction.prediction is True
    assert prediction.fraud_probability == 0.85

@pytest.mark.asyncio
async def test_get_prediction(test_db: AsyncSession):
    prediction_data = {
        "transaction_id": "TEST-DB-002",
        "prediction": False,
        "fraud_probability": 0.15,
        "risk_level": "LOW",
        "anomaly_score": 0.12,
        "threshold_used": 0.5,
        "model_version": "v1.0",
        "features": {"V1": 1.0}
    }
    
    created = await crud.create_prediction(test_db, **prediction_data)
    
    fetched = await crud.get_prediction(test_db, created.id)
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.transaction_id == "TEST-DB-002"

@pytest.mark.asyncio
async def test_get_prediction_by_transaction_id(test_db: AsyncSession):
    prediction_data = {
        "transaction_id": "TEST-DB-003",
        "prediction": True,
        "fraud_probability": 0.75,
        "risk_level": "HIGH",
        "anomaly_score": 0.8,
        "threshold_used": 0.5,
        "model_version": "v1.0",
        "features": {"V1": 1.0}
    }
    
    await crud.create_prediction(test_db, **prediction_data)
    
    fetched = await crud.get_prediction_by_transaction_id(test_db, "TEST-DB-003")
    
    assert fetched is not None
    assert fetched.transaction_id == "TEST-DB-003"

@pytest.mark.asyncio
async def test_get_predictions_pagination(test_db: AsyncSession):
    for i in range(5):
        await crud.create_prediction(
            test_db,
            transaction_id=f"TEST-DB-PAGE-{i}",
            prediction=i % 2 == 0,
            fraud_probability=0.5,
            risk_level="MEDIUM",
            anomaly_score=0.5,
            threshold_used=0.5,
            model_version="v1.0",
            features={"V1": 1.0}
        )
    
    predictions = await crud.get_predictions(test_db, skip=0, limit=3)
    assert len(predictions) <= 3

@pytest.mark.asyncio
async def test_get_predictions_fraud_only(test_db: AsyncSession):
    await crud.create_prediction(
        test_db,
        transaction_id="TEST-DB-FRAUD-1",
        prediction=True,
        fraud_probability=0.9,
        risk_level="HIGH",
        anomaly_score=0.9,
        threshold_used=0.5,
        model_version="v1.0",
        features={"V1": 1.0}
    )
    
    await crud.create_prediction(
        test_db,
        transaction_id="TEST-DB-NORMAL-1",
        prediction=False,
        fraud_probability=0.1,
        risk_level="LOW",
        anomaly_score=0.1,
        threshold_used=0.5,
        model_version="v1.0",
        features={"V1": 1.0}
    )
    
    fraud_predictions = await crud.get_predictions(test_db, fraud_only=True)
    
    assert all(p.prediction is True for p in fraud_predictions)

@pytest.mark.asyncio
async def test_create_feedback(test_db: AsyncSession):
    prediction_data = {
        "transaction_id": "TEST-DB-FB-001",
        "prediction": True,
        "fraud_probability": 0.8,
        "risk_level": "HIGH",
        "anomaly_score": 0.8,
        "threshold_used": 0.5,
        "model_version": "v1.0",
        "features": {"V1": 1.0}
    }
    
    prediction = await crud.create_prediction(test_db, **prediction_data)
    
    feedback = await crud.create_feedback(
        test_db,
        prediction_id=prediction.id,
        actual_label=False,
        feedback_source="manual",
        notes="False positive"
    )
    
    assert feedback.id is not None
    assert feedback.prediction_id == prediction.id
    assert feedback.actual_label is False
    assert feedback.notes == "False positive"

@pytest.mark.asyncio
async def test_log_api_usage(test_db: AsyncSession):
    usage = await crud.log_api_usage(
        test_db,
        api_key="test-key",
        endpoint="/api/v1/predict",
        method="POST",
        status_code=200,
        response_time_ms=150.5
    )
    
    assert usage.id is not None
    assert usage.api_key == "test-key"
    assert usage.endpoint == "/api/v1/predict"
    assert usage.response_time_ms == 150.5

@pytest.mark.asyncio
async def test_create_model_version(test_db: AsyncSession):
    version = await crud.create_model_version(
        test_db,
        version="v1.1",
        threshold=0.6,
        metrics={"recall": 0.85, "precision": 0.75},
        is_active=False
    )
    
    assert version.id is not None
    assert version.version == "v1.1"
    assert version.threshold == 0.6
    assert version.metrics["recall"] == 0.85

@pytest.mark.asyncio
async def test_get_active_model_version(test_db: AsyncSession):
    await crud.create_model_version(
        test_db,
        version="v2.0",
        threshold=0.5,
        metrics={"recall": 0.9},
        is_active=True
    )
    
    active = await crud.get_active_model_version(test_db)
    
    assert active is not None
    assert active.is_active is True
