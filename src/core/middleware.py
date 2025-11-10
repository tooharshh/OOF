import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.metrics import record_api_request
from src.core.logging_setup import log_api_request

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        duration_ms = duration * 1000
        
        record_api_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )
        
        log_api_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        
        return response
