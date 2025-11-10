from fastapi import HTTPException, Request
from typing import Callable
import time
from src.core.cache import cache
import structlog

logger = structlog.get_logger()

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 100,
        requests_per_hour: int = 1000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    async def check_rate_limit(self, api_key: str, endpoint: str):
        # If Redis is not available, skip rate limiting
        if not cache.redis_available:
            logger.debug("rate_limit_skipped", reason="redis_unavailable")
            return {
                "minute_remaining": self.requests_per_minute,
                "hour_remaining": self.requests_per_hour
            }
        
        current_time = int(time.time())
        
        minute_key = f"ratelimit:{api_key}:{endpoint}:minute:{current_time // 60}"
        hour_key = f"ratelimit:{api_key}:{endpoint}:hour:{current_time // 3600}"
        
        minute_count = await cache.incr(minute_key)
        if minute_count == 1:
            await cache.expire(minute_key, 60)
        
        if minute_count > self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
            )
        
        hour_count = await cache.incr(hour_key)
        if hour_count == 1:
            await cache.expire(hour_key, 3600)
        
        if hour_count > self.requests_per_hour:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
            )
        
        return {
            "minute_remaining": self.requests_per_minute - minute_count,
            "hour_remaining": self.requests_per_hour - hour_count
        }

rate_limiter = RateLimiter()

async def check_rate_limit(request: Request, api_key: str):
    endpoint = request.url.path
    return await rate_limiter.check_rate_limit(api_key, endpoint)
