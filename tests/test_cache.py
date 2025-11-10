import pytest
from src.core.cache import RedisCache, generate_cache_key

@pytest.mark.asyncio
async def test_redis_connection(redis_client: RedisCache):
    await redis_client.set("test_key", "test_value")
    value = await redis_client.get("test_key")
    assert value == "test_value"
    
    await redis_client.delete("test_key")
    value = await redis_client.get("test_key")
    assert value is None

@pytest.mark.asyncio
async def test_cache_expiration(redis_client: RedisCache):
    await redis_client.set("expire_key", "expire_value", ttl=1)
    
    value = await redis_client.get("expire_key")
    assert value == "expire_value"
    
    import asyncio
    await asyncio.sleep(2)
    
    value = await redis_client.get("expire_key")
    assert value is None

@pytest.mark.asyncio
async def test_cache_increment(redis_client: RedisCache):
    await redis_client.delete("counter_key")
    
    count1 = await redis_client.incr("counter_key")
    assert count1 == 1
    
    count2 = await redis_client.incr("counter_key")
    assert count2 == 2
    
    await redis_client.delete("counter_key")

@pytest.mark.asyncio
async def test_cache_ttl(redis_client: RedisCache):
    await redis_client.set("ttl_key", "ttl_value", ttl=60)
    
    ttl = await redis_client.ttl("ttl_key")
    assert ttl > 0
    assert ttl <= 60
    
    await redis_client.delete("ttl_key")

@pytest.mark.asyncio
async def test_cache_key_generation():
    key1 = generate_cache_key("test_func", arg1="value1", arg2="value2")
    key2 = generate_cache_key("test_func", arg1="value1", arg2="value2")
    key3 = generate_cache_key("test_func", arg1="different", arg2="value2")
    
    assert key1 == key2
    assert key1 != key3

@pytest.mark.asyncio
async def test_health_cache_operations(redis_client: RedisCache):
    from src.core.cache import set_health_cache, get_health_cache
    
    health_data = {"status": "healthy", "model_loaded": True}
    await set_health_cache(redis_client, health_data)
    
    cached_data = await get_health_cache(redis_client)
    assert cached_data == health_data

@pytest.mark.asyncio
async def test_cache_with_complex_data(redis_client: RedisCache):
    complex_data = {
        "prediction": True,
        "probability": 0.85,
        "details": {
            "risk_level": "HIGH",
            "threshold": 0.5
        }
    }
    
    await redis_client.set("complex_key", complex_data)
    retrieved = await redis_client.get("complex_key")
    
    assert retrieved == complex_data
    
    await redis_client.delete("complex_key")
