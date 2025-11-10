import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Fraud Detection API"
    assert "version" in data

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True

@pytest.mark.asyncio
async def test_predict_without_api_key(client: AsyncClient, sample_transaction):
    response = await client.post("/api/v1/predict", json=sample_transaction)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "fraud_predictions_total" in response.text