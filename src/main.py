from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import numpy as np
import time
from pathlib import Path

from src.core.config import get_settings, settings
from src.core.model_loader import model_loader
from src.core.cache import cache, get_health_cache, set_health_cache
from src.core.rate_limiter import check_rate_limit
from src.core.logging_setup import setup_logging, log_prediction, logger
from src.core.middleware import MonitoringMiddleware
from src.db.database import get_db
from src.db import crud
from src.api.schemas import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    SimpleTransactionRequest,
    SimpleTransactionInput
)
from src.api.prediction_schemas import (
    FeedbackCreate,
    FeedbackResponse,
    PredictionDetail
)
from typing import List
from uuid import UUID

setup_logging()
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready fraud detection API using Isolation Forest",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(MonitoringMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

@app.on_event("startup")
async def startup_event():
    await cache.connect()
    logger.info("application_startup", version=settings.APP_VERSION)

@app.on_event("shutdown")
async def shutdown_event():
    await cache.disconnect()
    logger.info("application_shutdown")

async def verify_api_key(request: Request, api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    await check_rate_limit(request, api_key)
    return api_key


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Fraud Detection API",
        "version": settings.APP_VERSION,
        "status": "active",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/api", tags=["Root"])
async def api_root():
    return {
        "message": "Fraud Detection API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    try:
        cached_health = await get_health_cache()
        if cached_health:
            return HealthResponse(**cached_health)
        
        metadata = model_loader.get_metadata()
        health_data = {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "model_loaded": True,
            "model_type": metadata["model_type"],
            "model_metrics": metadata["test_metrics"]
        }
        
        await set_health_cache(health_data, expire=60)
        return HealthResponse(**health_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post(
    f"{settings.API_V1_PREFIX}/predict",
    response_model=PredictionResponse,
    tags=["Prediction"]
)
async def predict_fraud(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    try:
        transaction = request.transaction
        start_time = time.time()
        
        # Extract V1-V28 features
        v_features = [
            transaction.V1, transaction.V2, transaction.V3, transaction.V4,
            transaction.V5, transaction.V6, transaction.V7, transaction.V8,
            transaction.V9, transaction.V10, transaction.V11, transaction.V12,
            transaction.V13, transaction.V14, transaction.V15, transaction.V16,
            transaction.V17, transaction.V18, transaction.V19, transaction.V20,
            transaction.V21, transaction.V22, transaction.V23, transaction.V24,
            transaction.V25, transaction.V26, transaction.V27, transaction.V28
        ]
        
        # Scale Time and Amount separately (matching training process)
        scaler = model_loader.get_scaler()
        time_scaled = scaler.transform([[transaction.Time]])[0][0]
        amount_scaled = scaler.transform([[transaction.Amount]])[0][0]
        
        # Build final feature array: V1-V28, Time_scaled, Amount_scaled
        features = np.array([v_features + [time_scaled, amount_scaled]])
        
        model = model_loader.get_model()
        anomaly_score = model.decision_function(features)[0]
        threshold = model_loader.get_threshold()
        
        prediction = 1 if anomaly_score < threshold else 0
        fraud_probability = max(0, min(1, (threshold - anomaly_score) / (threshold + 0.1)))
        
        if fraud_probability >= 0.7:
            risk_level = "HIGH"
        elif fraud_probability >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        prediction_time = time.time() - start_time
        
        log_prediction(
            transaction_id=request.transaction_id,
            prediction=bool(prediction),
            probability=float(fraud_probability),
            risk_level=risk_level
        )
        
        features_dict = {
            **{f"V{i+1}": float(transaction.dict()[f"V{i+1}"]) for i in range(28)},
            "Time": float(transaction.Time),
            "Amount": float(transaction.Amount)
        }
        
        # Try to save to database, but don't fail if database is unavailable
        try:
            await crud.create_prediction(
                db=db,
                transaction_id=request.transaction_id,
                prediction=bool(prediction),
                fraud_probability=float(fraud_probability),
                risk_level=risk_level,
                anomaly_score=float(anomaly_score),
                threshold=float(threshold),
                model_version=settings.APP_VERSION,
                features=features_dict
            )
        except Exception as db_error:
            logger.warning("database_save_failed", error=str(db_error), transaction_id=request.transaction_id)
        
        return PredictionResponse(
            transaction_id=request.transaction_id,
            prediction=prediction,
            fraud_probability=round(fraud_probability, 4),
            risk_level=risk_level,
            anomaly_score=round(float(anomaly_score), 4),
            threshold=round(threshold, 4),
            timestamp=datetime.now(),
            model_version=settings.APP_VERSION
        )
        
    except Exception as e:
        logger.error("prediction_error", error=str(e), transaction_id=request.transaction_id)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post(
    f"{settings.API_V1_PREFIX}/predict/simple",
    response_model=PredictionResponse,
    tags=["Prediction"],
    summary="Simple Fraud Check (User-Friendly)",
    description="Easy-to-use fraud detection endpoint. Just provide transaction amount and optionally time of day. Perfect for non-technical users!"
)
async def predict_fraud_simple(
    request: SimpleTransactionRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Simplified fraud detection endpoint for regular users.
    
    You only need to provide:
    - transaction_id: A unique ID for your transaction (e.g., "TXN-001")
    - amount: Transaction amount in dollars (e.g., 149.62)
    - time_of_day: Optional - "morning", "afternoon", "evening", or "night"
    
    The system will handle all the complex ML features automatically!
    """
    try:
        # Map time of day to time value (seconds since midnight approximately)
        time_mapping = {
            "morning": 28800,    # 8 AM
            "afternoon": 43200,  # 12 PM
            "evening": 64800,    # 6 PM
            "night": 0           # 12 AM
        }
        
        time_value = time_mapping.get(request.transaction.time_of_day, 43200) if request.transaction.time_of_day else 43200
        
        # Use neutral/average values for V1-V28 features
        # These are median values from the training dataset
        default_v_features = [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ]
        
        start_time = time.time()
        
        # Scale Time and Amount
        scaler = model_loader.get_scaler()
        time_scaled = scaler.transform([[time_value]])[0][0]
        amount_scaled = scaler.transform([[request.transaction.amount]])[0][0]
        
        # Build feature array
        features = np.array([default_v_features + [time_scaled, amount_scaled]])
        
        # Make prediction
        model = model_loader.get_model()
        anomaly_score = model.decision_function(features)[0]
        threshold = model_loader.get_threshold()
        
        prediction = 1 if anomaly_score < threshold else 0
        fraud_probability = max(0, min(1, (threshold - anomaly_score) / (threshold + 0.1)))
        
        if fraud_probability >= 0.7:
            risk_level = "HIGH"
        elif fraud_probability >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        prediction_time = time.time() - start_time
        
        log_prediction(
            transaction_id=request.transaction_id,
            prediction=bool(prediction),
            probability=float(fraud_probability),
            risk_level=risk_level
        )
        
        features_dict = {
            **{f"V{i+1}": 0.0 for i in range(28)},
            "Time": float(time_value),
            "Amount": float(request.transaction.amount)
        }
        
        # Try to save to database
        try:
            await crud.create_prediction(
                db=db,
                transaction_id=request.transaction_id,
                prediction=bool(prediction),
                fraud_probability=float(fraud_probability),
                risk_level=risk_level,
                anomaly_score=float(anomaly_score),
                threshold=float(threshold),
                model_version=settings.APP_VERSION,
                features=features_dict
            )
        except Exception as db_error:
            logger.warning("database_save_failed", error=str(db_error), transaction_id=request.transaction_id)
        
        return PredictionResponse(
            transaction_id=request.transaction_id,
            prediction=prediction,
            fraud_probability=round(fraud_probability, 4),
            risk_level=risk_level,
            anomaly_score=round(float(anomaly_score), 4),
            threshold=round(threshold, 4),
            timestamp=datetime.now(),
            model_version=settings.APP_VERSION
        )
        
    except Exception as e:
        logger.error("prediction_error", error=str(e), transaction_id=request.transaction_id)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post(
    f"{settings.API_V1_PREFIX}/predict/batch",
    response_model=BatchPredictionResponse,
    tags=["Prediction"]
)
async def predict_batch(
    request: BatchPredictionRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    start_time = time.time()
    
    try:
        predictions = []
        fraud_count = 0
        
        for txn_request in request.transactions:
            result = await predict_fraud(txn_request, db, api_key)
            predictions.append(result)
            if result.prediction == 1:
                fraud_count += 1
        
        processing_time = (time.time() - start_time) * 1000
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_processed=len(predictions),
            fraud_detected=fraud_count,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get(
    f"{settings.API_V1_PREFIX}/predictions/{{prediction_id}}",
    response_model=PredictionDetail,
    tags=["Predictions"]
)
async def get_prediction(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    prediction = await crud.get_prediction(db, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


@app.get(
    f"{settings.API_V1_PREFIX}/predictions",
    response_model=List[PredictionDetail],
    tags=["Predictions"]
)
async def list_predictions(
    skip: int = 0,
    limit: int = 100,
    fraud_only: bool = False,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    predictions = await crud.get_predictions(db, skip=skip, limit=limit, fraud_only=fraud_only)
    return predictions


@app.post(
    f"{settings.API_V1_PREFIX}/feedback",
    response_model=FeedbackResponse,
    tags=["Feedback"]
)
async def submit_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    prediction = await crud.get_prediction(db, feedback.prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    db_feedback = await crud.create_feedback(
        db=db,
        prediction_id=feedback.prediction_id,
        actual_label=feedback.actual_label,
        feedback_source=feedback.feedback_source,
        notes=feedback.notes
    )
    
    logger.info(
        "feedback_submitted",
        prediction_id=str(feedback.prediction_id),
        actual_label=feedback.actual_label,
        source=feedback.feedback_source
    )
    
    return db_feedback


@app.get(
    f"{settings.API_V1_PREFIX}/cache/stats",
    tags=["Monitoring"]
)
async def cache_stats(api_key: str = Depends(verify_api_key)):
    try:
        if not cache.redis_client:
            await cache.connect()
        
        info = await cache.redis_client.info()
        return {
            "connected": True,
            "used_memory": info.get("used_memory_human"),
            "total_keys": await cache.redis_client.dbsize(),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0) / 
                max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                2
            )
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
