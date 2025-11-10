import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import crud

@pytest.mark.asyncio
async def test_complete_prediction_workflow(
    client: AsyncClient,
    test_db: AsyncSession,
    sample_transaction,
    headers
):
    response = await client.post(
        "/api/v1/predict",
        json=sample_transaction,
        headers=headers
    )
    
    assert response.status_code == 200
    prediction_result = response.json()
    
    assert "transaction_id" in prediction_result
    assert "prediction" in prediction_result
    
    db_prediction = await crud.get_prediction_by_transaction_id(
        test_db,
        sample_transaction["transaction_id"]
    )
    
    assert db_prediction is not None
    assert db_prediction.transaction_id == sample_transaction["transaction_id"]

@pytest.mark.asyncio
async def test_prediction_and_feedback_workflow(
    client: AsyncClient,
    test_db: AsyncSession,
    sample_transaction,
    headers
):
    predict_response = await client.post(
        "/api/v1/predict",
        json=sample_transaction,
        headers=headers
    )
    assert predict_response.status_code == 200
    
    db_prediction = await crud.get_prediction_by_transaction_id(
        test_db,
        sample_transaction["transaction_id"]
    )
    
    feedback_data = {
        "prediction_id": db_prediction.id,
        "actual_label": False,
        "feedback_source": "customer",
        "notes": "Customer confirmed this was a legitimate transaction"
    }
    
    feedback_response = await client.post(
        "/api/v1/feedback",
        json=feedback_data,
        headers=headers
    )
    
    assert feedback_response.status_code == 200

@pytest.mark.asyncio
async def test_batch_prediction_workflow(
    client: AsyncClient,
    test_db: AsyncSession,
    sample_transaction,
    headers
):
    transaction1 = sample_transaction.copy()
    transaction1["transaction_id"] = "BATCH-001"
    
    transaction2 = sample_transaction.copy()
    transaction2["transaction_id"] = "BATCH-002"
    
    batch_data = {"transactions": [transaction1, transaction2]}
    
    response = await client.post(
        "/api/v1/predict/batch",
        json=batch_data,
        headers=headers
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["total_processed"] == 2
    
    db_pred1 = await crud.get_prediction_by_transaction_id(test_db, "BATCH-001")
    db_pred2 = await crud.get_prediction_by_transaction_id(test_db, "BATCH-002")
    
    assert db_pred1 is not None
    assert db_pred2 is not None

@pytest.mark.asyncio
async def test_cached_health_check_workflow(
    client: AsyncClient,
    redis_client
):
    from src.core.cache import get_health_cache
    
    cached = await get_health_cache(redis_client)
    assert cached is None
    
    response1 = await client.get("/health")
    assert response1.status_code == 200
    
    cached = await get_health_cache(redis_client)
    assert cached is not None
    
    response2 = await client.get("/health")
    assert response2.status_code == 200
    assert response1.json() == response2.json()

@pytest.mark.asyncio
async def test_api_usage_tracking_workflow(
    client: AsyncClient,
    test_db: AsyncSession,
    sample_transaction,
    headers
):
    initial_count = len(await test_db.execute(
        "SELECT * FROM api_usage WHERE api_key = :key",
        {"key": headers["X-API-Key"]}
    ))
    
    await client.post("/api/v1/predict", json=sample_transaction, headers=headers)
    
    final_count = len(await test_db.execute(
        "SELECT * FROM api_usage WHERE api_key = :key",
        {"key": headers["X-API-Key"]}
    ))
    
    assert final_count > initial_count

@pytest.mark.asyncio
async def test_metrics_collection_workflow(client: AsyncClient):
    initial_metrics = await client.get("/metrics")
    assert initial_metrics.status_code == 200
    
    await client.get("/health")
    
    final_metrics = await client.get("/metrics")
    assert final_metrics.status_code == 200
    assert len(final_metrics.text) > len(initial_metrics.text)

@pytest.mark.asyncio
async def test_error_handling_workflow(
    client: AsyncClient,
    headers
):
    invalid_data = {
        "transaction_id": "ERROR-001",
        "transaction": {"invalid": "data"}
    }
    
    response = await client.post("/api/v1/predict", json=invalid_data, headers=headers)
    assert response.status_code == 422
    
    metrics_response = await client.get("/metrics")
    assert "fraud_predictions_total" in metrics_response.text
