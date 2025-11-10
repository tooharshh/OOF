import redis.asyncio as redis
import json
import hashlib
from typing import Optional, Any
from functools import wraps
from src.core.config import settings
import structlog

logger = structlog.get_logger()

class RedisCache:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.redis_available = True
    
    async def connect(self):
        if not self.redis_client and self.redis_available:
            try:
                self.redis_client = await redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("redis_connected", host=settings.REDIS_HOST, port=settings.REDIS_PORT)
            except Exception as e:
                logger.warning("redis_connection_failed", error=str(e), message="Running without Redis cache")
                self.redis_available = False
                self.redis_client = None
    
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str) -> Optional[str]:
        if not self.redis_available:
            return None
        if not self.redis_client:
            await self.connect()
        if not self.redis_available:
            return None
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.warning("redis_get_failed", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, expire: int = None):
        if not self.redis_available:
            return
        if not self.redis_client:
            await self.connect()
        if not self.redis_available:
            return
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                await self.redis_client.setex(key, expire, value)
            else:
                await self.redis_client.set(key, value)
        except Exception as e:
            logger.warning("redis_set_failed", key=key, error=str(e))
    
    async def delete(self, key: str):
        if not self.redis_available:
            return
        if not self.redis_client:
            await self.connect()
        if not self.redis_available:
            return
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.warning("redis_delete_failed", key=key, error=str(e))
    
    async def exists(self, key: str) -> bool:
        if not self.redis_available:
            return False
        if not self.redis_client:
            await self.connect()
        if not self.redis_available:
            return False
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.warning("redis_exists_failed", key=key, error=str(e))
            return False
    
    async def incr(self, key: str, amount: int = 1) -> int:
        if not self.redis_available:
            return 1  # Return 1 to simulate first increment when Redis is unavailable
        if not self.redis_client:
            await self.connect()
        if not self.redis_available:
            return 1
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.warning("redis_incr_failed", key=key, error=str(e))
            return 1
    
    async def expire(self, key: str, seconds: int):
        if not self.redis_available:
            return
        if not self.redis_client:
            await self.connect()
        if not self.redis_available:
            return
        try:
            await self.redis_client.expire(key, seconds)
        except Exception as e:
            logger.warning("redis_expire_failed", key=key, error=str(e))
    
    async def ttl(self, key: str) -> int:
        if not self.redis_available:
            return -1
        if not self.redis_client:
            await self.connect()
        if not self.redis_available:
            return -1
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.warning("redis_ttl_failed", key=key, error=str(e))
            return -1

cache = RedisCache()

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    key_parts = [prefix]
    
    for arg in args:
        if isinstance(arg, (dict, list)):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (dict, list)):
            key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        else:
            key_parts.append(f"{k}:{v}")
    
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cache_prediction(expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or args[0]
            features_dict = request.transaction.dict()
            cache_key = f"prediction:{generate_cache_key('pred', features_dict)}"
            
            cached = await cache.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result.dict(), expire=expire)
            
            return result
        
        return wrapper
    return decorator

async def get_health_cache() -> Optional[dict]:
    cached = await cache.get("health:status")
    if cached:
        return json.loads(cached)
    return None

async def set_health_cache(data: dict, expire: int = 60):
    await cache.set("health:status", data, expire=expire)
