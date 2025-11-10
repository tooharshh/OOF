# OOF

A production-ready fraud detection system using Machine Learning (Isolation Forest) deployed as a scalable REST API with PostgreSQL, Redis caching, and comprehensive monitoring.

## About

--> I built this project to understand how machine learning can be applied to real-world fraud detection problems. The challenge was interesting because fraud cases are extremely rare, which led me to explore anomaly detection techniques, specifically Isolation Forest, which worked really well for this use case. 
--> The API is built with FastAPI, stores predictions in PostgreSQL, implements rate limiting with Redis, and provides monitoring through Prometheus and Grafana.
## About the Dataset

The dataset I used is the [Credit Card Fraud Detection Dataset](https://www.kaggle.com/datasets/kartik2112/fraud-detection). What makes this dataset challenging and realistic is that it's highly imbalanced - only 492 transactions out of 284,807 are fraudulent, which is just 0.172% of the total.

## Model Training Results

The Isolation Forest model achieved:

| Metric | Score | Description |
|--------|-------|-------------|
| **ROC-AUC** | 95.3% | Excellent ability to distinguish fraud from legitimate transactions |
| **Recall** | 81.63% | Successfully catches 82% of all fraudulent transactions |
| **Precision** | 6.61% | Trade-off made to maximize fraud detection |
| **F1-Score** | 0.122 | Balanced measure of precision and recall |
| **Training Time** | ~8 seconds | Fast training on entire dataset |
| **Inference Time** | <50ms | Real-time prediction capability |

The model was trained with these parameters:
- **n_estimators**: 100 (number of trees in the forest)
- **max_samples**: 256 (samples used to build each tree)
- **contamination**: 0.002 (expected proportion of outliers)
- **random_state**: 42 (for reproducibility)

I spent a lot of time optimizing the decision threshold. The default threshold didn't work well for such an imbalanced dataset, so I tested different thresholds and settled on one that balanced catching most frauds while keeping false positives manageable for a real-world scenario.

## Problems I Faced

### 1. Extreme Class Imbalance
The biggest challenge was dealing with only 0.172% fraud cases. Traditional classification algorithms were just predicting everything as "not fraud" because that would give 99.8% accuracy. I tried several approaches:
- Initially attempted Logistic Regression and Random Forest - both struggled with the imbalance
- Experimented with SMOTE (Synthetic Minority Over-sampling) but it created artificial patterns
- Finally settled on Isolation Forest because it's specifically designed to detect anomalies without needing balanced classes

### 2. Threshold Optimization
The model outputs an anomaly score, but deciding when to flag something as fraud was tricky. Setting the threshold too low meant too many false alarms, too high meant missing real fraud. I created a script to test different thresholds and visualize the trade-off between recall and precision. Eventually found a sweet spot where we catch 81% of frauds while keeping the system practical.

### 3. Feature Scaling
The 'Time' and 'Amount' features had very different scales compared to the PCA-transformed features. Initially, the model was giving too much weight to these unscaled features. I solved this by applying StandardScaler to normalize them before training.

### 4. Real-time Performance
Getting predictions under 100ms was important for a production system. The initial model was taking 200-300ms per prediction. I optimized this by:
- Using Redis caching for repeat predictions
- Implementing database connection pooling
- Loading the model once at startup instead of per-request
- Using async database operations

### 5. Database Migrations
Setting up Alembic migrations was frustrating at first. I had to learn how to properly handle schema changes, especially when I needed to add the feedback table later in development. Eventually got comfortable with the migration workflow.

## Future Prospects

Right now the API runs locally with Docker, but I'm planning to deploy it to the cloud. Here are some ideas I'm considering:

### Deployment Plans
- **AWS Elastic Beanstalk** or **Google Cloud Run** for easy managed deployment
- Set up CI/CD pipeline with GitHub Actions for automated testing and deployment
- Use AWS RDS or Cloud SQL for managed PostgreSQL instead of self-hosted
- Implement proper secrets management with AWS Secrets Manager or similar

### Model Improvements
- Retrain the model with more recent data to catch evolving fraud patterns
- Experiment with ensemble methods combining Isolation Forest with other algorithms
- Add more features if available (merchant info, location data, customer history)
- Implement automated model retraining based on feedback data

### System Enhancements
- Add a proper admin dashboard for monitoring predictions and system health
- Build a feedback loop where confirmed fraud cases help retrain the model
- Implement A/B testing to compare different model versions in production
- Add email/SMS alerts for high-risk transactions

### Scalability
- Move to Kubernetes for better container orchestration
- Implement horizontal scaling for handling more requests
- Add a message queue (RabbitMQ/Kafka) for batch processing
- Consider using a feature store for managing ML features

## Built With

- **Python 3.13** - Programming language
- **FastAPI** - Web framework for building the API
- **scikit-learn** - Machine learning library (Isolation Forest)
- **PostgreSQL** - Database for storing predictions
- **Redis** - Caching and rate limiting
- **Docker** - Containerization
- **Prometheus & Grafana** - Monitoring and visualization
- **SQLAlchemy** - Database ORM
- **Alembic** - Database migrations
- **pytest** - Testing framework



## Architecture

The system follows a microservices architecture with clear separation of concerns:

```
Client Request
     |
     v
NGINX (Reverse Proxy)
     |
     v
FastAPI Application
     |
     +-- Redis (Rate Limiting & Caching)
     |
     +-- ML Model (Isolation Forest)
     |
     +-- PostgreSQL (Predictions Storage)
     |
     +-- Prometheus (Metrics)
```

When a prediction request comes in, it first goes through rate limiting checks using Redis. If approved, the transaction data is normalized using the pre-trained scaler, then passed to the Isolation Forest model. The prediction is stored in PostgreSQL for tracking and analysis, and metrics are sent to Prometheus for monitoring.

### Technology Stack

- **Backend**: FastAPI 0.115.0, Python 3.13.9
- **Database**: PostgreSQL 13 with async SQLAlchemy
- **Cache**: Redis 6 (rate limiting, health check caching)
- **ML**: scikit-learn 1.5.2 (Isolation Forest)
- **Monitoring**: Prometheus, Grafana
- **Deployment**: Docker, Docker Compose
- **Testing**: pytest, pytest-asyncio

## Getting Started

### Prerequisites

- Python 3.13.9
- Docker and Docker Compose
- PostgreSQL 13 (if running without Docker)
- Redis 6 (if running without Docker)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tooharshh/fault_detection.git
cd fault_detection
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start infrastructure with Docker:
```bash
docker compose up -d postgres redis
```

6. Run database migrations:
```bash
alembic upgrade head
```

7. Start the API:
```bash
python start_api.py
```

The API will be available at http://localhost:8000

> **Note**: If you run into any issues with the database connection, make sure PostgreSQL and Redis are running first. You can check with `docker ps` to see if the containers are up.

### Quick Start with Docker

Start all services with a single command:

```bash
docker compose up -d
```

Access the services:
- API Documentation: http://localhost:8000/docs
- Web UI: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- pgAdmin: http://localhost:5050

The Swagger UI at `/docs` is really helpful for testing the API without writing any code. You can try out all the endpoints directly from your browser.

## API Documentation

### Authentication

All API endpoints (except /health and /) require an API key in the request header:

```
X-API-Key: your-api-key-here
```

### Core Endpoints

#### Health Check
```http
GET /health
```

Returns system health status and model metrics.

#### Single Prediction
```http
POST /api/v1/predict
Content-Type: application/json
X-API-Key: dev-key-12345

{
  "transaction_id": "TXN-001",
  "transaction": {
    "V1": -1.359807,
    "V2": -0.072781,
    ...
    "V28": -0.021053,
    "Time": 0.0,
    "Amount": 149.62
  }
}
```

Response:
```json
{
  "transaction_id": "TXN-001",
  "prediction": 0,
  "fraud_probability": 0.15,
  "risk_level": "LOW",
  "anomaly_score": 0.2676,
  "threshold": 0.1284,
  "timestamp": "2025-11-10T10:30:00",
  "model_version": "1.0.0"
}
```

#### Batch Predictions
```http
POST /api/v1/predict/batch
Content-Type: application/json
X-API-Key: dev-key-12345

{
  "transactions": [
    {
      "transaction_id": "TXN-001",
      "transaction": {...}
    },
    {
      "transaction_id": "TXN-002",
      "transaction": {...}
    }
  ]
}
```

#### List Predictions
```http
GET /api/v1/predictions?skip=0&limit=100&fraud_only=false
X-API-Key: dev-key-12345
```

#### Get Prediction by ID
```http
GET /api/v1/predictions/{prediction_id}
X-API-Key: dev-key-12345
```

#### Submit Feedback
```http
POST /api/v1/feedback
Content-Type: application/json
X-API-Key: dev-key-12345

{
  "prediction_id": "uuid-here",
  "actual_label": true,
  "feedback_source": "manual_review",
  "notes": "Confirmed fraud case"
}
```

### Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per minute per API key
- 1000 requests per hour per API key
- Returns HTTP 429 when limit exceeded

If you hit the rate limit during testing, just wait a minute or adjust the limits in the configuration.

## Database Schema

### Predictions Table
```sql
CREATE TABLE predictions (
    id UUID PRIMARY KEY,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    prediction BOOLEAN NOT NULL,
    fraud_probability FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    anomaly_score FLOAT NOT NULL,
    threshold_used FLOAT NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    features JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Feedback Table
```sql
CREATE TABLE feedback (
    id UUID PRIMARY KEY,
    prediction_id UUID REFERENCES predictions(id),
    actual_label BOOLEAN NOT NULL,
    feedback_source VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL
);
```

The feedback table is crucial for improving the model over time. Every time someone confirms whether a prediction was correct or not, that information is stored and can be used for retraining.

## Machine Learning Model

### Why Isolation Forest?

I chose Isolation Forest for several reasons:

1. **Handles Imbalanced Data**: With only 0.17% fraud cases, traditional classifiers don't work well
2. **Unsupervised Learning**: Doesn't require perfectly labeled fraud examples to learn patterns
3. **Fast Inference**: O(log n) complexity means predictions are really fast
4. **Robust to Outliers**: Specifically designed to identify anomalies
5. **Good Performance**: Achieved 95.3% ROC-AUC score

The algorithm works by randomly selecting features and split values to isolate observations. Anomalies (fraudulent transactions) are easier to isolate and require fewer splits, resulting in shorter path lengths in the isolation trees.

### Dataset

Source: [Kaggle Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)

- 284,807 transactions
- 492 fraudulent (0.172% fraud rate)
- 30 features (V1-V28 PCA transformed, Time, Amount)

### Model Training

The model training process is documented in `model.ipynb`:

1. Exploratory Data Analysis
2. Feature Engineering (StandardScaler for Time and Amount)
3. Isolation Forest training
4. Threshold optimization for balanced recall/precision
5. Model evaluation on test set

The notebook includes visualizations showing transaction patterns, time-based analysis, and model performance metrics. I spent a lot of time on the threshold optimization step because it has a huge impact on the model's practical usefulness.

### Model Selection: Why Isolation Forest?

Isolation Forest was chosen because:

1. **Imbalanced Data**: Only 0.17% of transactions are fraudulent
2. **Unsupervised Learning**: Doesn't require labeled fraud examples
3. **Fast Inference**: O(log n) complexity, suitable for real-time detection
4. **Robust to Outliers**: Designed to identify anomalies
5. **High Performance**: 95.3% ROC-AUC score

### Feature Engineering

The features are processed before being fed to the model:
- V1-V28: PCA-transformed features (used as-is, already normalized)
- Time: Scaled using StandardScaler to match the range of other features
- Amount: Scaled using StandardScaler to prevent bias toward large transactions

Initially I wasn't scaling Time and Amount, and the model was giving them too much importance just because they had larger values. StandardScaler fixed this issue.

## Development

### Project Structure

```
fault_detection/
├── app/
│   ├── api/
│   │   ├── schemas.py              # Pydantic request/response models
│   │   └── prediction_schemas.py   # Prediction-related schemas
│   ├── core/
│   │   ├── config.py               # Application configuration
│   │   ├── model_loader.py         # ML model singleton
│   │   ├── cache.py                # Redis cache implementation
│   │   ├── rate_limiter.py         # Rate limiting logic
│   │   ├── logging_setup.py        # Structured logging
│   │   ├── metrics.py              # Prometheus metrics
│   │   └── middleware.py           # Request monitoring
│   ├── db/
│   │   ├── database.py             # Database connection
│   │   ├── models.py               # SQLAlchemy models
│   │   └── crud.py                 # Database operations
│   ├── static/                     # Web UI assets
│   ├── templates/                  # Web UI HTML
│   └── main.py                     # FastAPI application
├── models/
│   ├── isolation_forest_model.pkl  # Trained ML model
│   ├── scaler.pkl                  # Feature scaler
│   └── model_metadata.json         # Model metrics
├── alembic/
│   └── versions/                   # Database migrations
├── tests/
│   ├── test_api.py                 # API endpoint tests
│   ├── test_models.py              # ML model tests
│   ├── test_database.py            # Database tests
│   ├── test_cache.py               # Cache tests
│   └── test_integration.py         # Integration tests
├── docker-compose.yml              # Multi-service orchestration
├── Dockerfile                      # API container definition
├── requirements.txt                # Python dependencies
├── alembic.ini                     # Alembic configuration
├── start_api.py                    # API startup script
└── model.ipynb                     # Model training notebook
```

### Running Tests

Run the test suite to make sure everything is working:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

I've included tests for the API endpoints, database operations, caching, and model predictions. The coverage isn't 100% yet, but it covers all the critical paths.

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

Alembic has been really useful for managing database schema changes without losing data. It auto-generates migrations by comparing your SQLAlchemy models to the current database schema.

## Deployment

### Docker Deployment

The application uses Docker with a multi-stage build for optimization:

```bash
# Build the image
docker build -t fraud-detection-api .

# Run with Docker Compose
docker compose up -d
```

Docker Compose sets up the entire stack (API, PostgreSQL, Redis, Prometheus, Grafana) with a single command, which makes local development and testing much easier.

### Environment Variables

Required environment variables (`.env` file):

```bash
# Application
APP_NAME=Fraud Detection API
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# API
API_KEY=your-secure-api-key-here
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://fraud_user:fraud_pass@localhost:5432/fraud_detection

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_EXPIRATION=3600

# Model Paths
MODEL_PATH=models/isolation_forest_model.pkl
SCALER_PATH=models/scaler.pkl
METADATA_PATH=models/model_metadata.json

# Monitoring
ENABLE_METRICS=True
```

Make sure to change the API_KEY and SECRET_KEY in production. The default values are only for development.

### Cloud Deployment Options

#### AWS
- Elastic Beanstalk (managed)
- ECS Fargate (containerized)
- EC2 (full control)

#### Google Cloud Platform
- Cloud Run (serverless)
- GKE (Kubernetes)
- Compute Engine (VMs)

#### Azure
- App Service
- Container Instances
- AKS (Kubernetes)

I'm leaning toward using Google Cloud Run or AWS Elastic Beanstalk for the first deployment because they handle a lot of the infrastructure management automatically.

### Production Checklist

- [ ] Generate secure API keys
- [ ] Set DEBUG=False
- [ ] Configure SSL/TLS certificates
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Set up monitoring alerts
- [ ] Implement CI/CD pipeline
- [ ] Perform load testing
- [ ] Document disaster recovery plan
- [ ] Enable database connection pooling

This checklist helps ensure nothing important is missed when moving to production. I learned the hard way that skipping any of these can cause issues later.

## Monitoring

### Prometheus Metrics

The API exposes Prometheus metrics at `/metrics`:

- `fraud_predictions_total`: Total predictions made
- `fraud_detection_latency`: Prediction response time
- `api_requests_total`: Total API requests
- `fraud_by_risk_level`: Predictions by risk level

These metrics help track how the system is performing in production and can trigger alerts if something goes wrong.

### Grafana Dashboards

Pre-configured dashboards for:
- API request rates
- Prediction latency (p50, p95, p99)
- Fraud detection rate
- Cache hit rate
- Database query performance

Access Grafana at http://localhost:3000 (default credentials: admin/admin)

The dashboards give a nice visual overview of what's happening with the API. You can see request spikes, slow queries, and fraud detection patterns over time.

### Logging

Structured JSON logging to stdout:

```json
{
  "event": "prediction",
  "transaction_id": "TXN-001",
  "prediction": false,
  "fraud_probability": 0.15,
  "risk_level": "LOW",
  "timestamp": "2025-11-10T10:30:00Z",
  "level": "info"
}
```

JSON logs are easier to parse and search through, especially when using log aggregation tools like ELK stack or CloudWatch.

## Acknowledgments

I used the [Kaggle Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) dataset for training the model. Big thanks to the dataset creators for making this available for research and learning purposes.
