from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Counters
predictions_total = Counter(
    'fraud_predictions_total',
    'Total number of fraud predictions made',
    ['prediction', 'risk_level']
)

predictions_fraud_detected = Counter(
    'fraud_detected_total',
    'Total number of frauds detected'
)

api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

cache_operations = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

feedback_submitted = Counter(
    'feedback_submitted_total',
    'Total feedback submissions',
    ['actual_label']
)

# Histograms
prediction_duration = Histogram(
    'prediction_duration_seconds',
    'Time spent making predictions',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['operation'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Gauges
active_predictions = Gauge(
    'active_predictions',
    'Number of predictions currently being processed'
)

cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate percentage'
)

model_threshold = Gauge(
    'model_threshold',
    'Current model threshold'
)

def record_prediction(prediction: bool, risk_level: str, duration: float):
    """Record prediction metrics"""
    predictions_total.labels(
        prediction='fraud' if prediction else 'legitimate',
        risk_level=risk_level
    ).inc()
    
    if prediction:
        predictions_fraud_detected.inc()
    
    prediction_duration.observe(duration)

def record_api_request(method: str, endpoint: str, status: int, duration: float):
    """Record API request metrics"""
    api_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status)
    ).inc()
    
    api_request_duration.labels(endpoint=endpoint).observe(duration)

def record_cache_operation(operation: str, hit: bool = None):
    """Record cache operation metrics"""
    result = 'hit' if hit else 'miss' if hit is not None else 'write'
    cache_operations.labels(
        operation=operation,
        result=result
    ).inc()

def record_db_query(operation: str, duration: float):
    """Record database query metrics"""
    db_query_duration.labels(operation=operation).observe(duration)

def record_feedback(actual_label: bool):
    """Record feedback submission"""
    feedback_submitted.labels(
        actual_label='fraud' if actual_label else 'legitimate'
    ).inc()

async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
