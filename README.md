# OOF

A production-ready fraud detection system using Machine Learning (Isolation Forest) deployed as a scalable REST API with PostgreSQL and Redis caching.

## About

--> I built this project to understand how machine learning can be applied to real-world fraud detection problems. The challenge was interesting because fraud cases are extremely rare, which led me to explore anomaly detection techniques, specifically Isolation Forest, which worked really well for this use case. 

--> The API is built with FastAPI, stores predictions in PostgreSQL, and implements rate limiting with Redis.

## About the Dataset

The dataset I used is the [Credit Card Fraud Detection Dataset](https://www.kaggle.com/datasets/kartik2112/fraud-detection). What makes this dataset challenging and realistic is that it's highly imbalanced - only 492 transactions out of 284,807 are fraudulent, which is just 0.172% of the total.

## Model Training Results

The Isolation Forest model achieved:

| Metric | Score |
|--------|-------|
| **ROC-AUC** | 95.3% |
| **Recall** | 81.63% |
| **Precision** | 6.61% |
| **F1-Score** | 0.122 |
| **Training Time** | ~8 seconds |
| **Inference Time** | <50ms |

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
Planning to use AWS Elastic Beanstalk or Google Cloud Run for managed deployment. Will set up GitHub Actions for CI/CD, migrate to managed databases like RDS or Cloud SQL, and implement proper secrets management.

### Model Improvements
I want to experiment with ensemble methods like XGBoost and LightGBM, and also try deep learning approaches using Autoencoders for anomaly detection. 

### Scalability
Moving to Kubernetes for better orchestration and implementing horizontal scaling. Adding a message queue like RabbitMQ or Kafka for batch processing would help handle larger volumes. A feature store could streamline ML feature management.

## Built With

- **Python 3.13**
- **FastAPI** - 
- **scikit-learn** 
- **PostgreSQL** 
- **Redis** 
- **Docker** 
- **SQLAlchemy** 
- **Alembic** 
- **pytest**



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
```

When a prediction request comes in, it first goes through rate limiting checks using Redis. If approved, the transaction data is normalized using the pre-trained scaler, then passed to the Isolation Forest model. The prediction is stored in PostgreSQL for tracking and analysis.

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


### Running Tests

Run the test suite to make sure everything is working:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run tests in Docker
docker compose exec api pytest tests/ -v
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

Docker Compose sets up the entire stack (API, PostgreSQL, Redis) with a single command, which makes local development and testing much easier.

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
```

Make sure to change the API_KEY and SECRET_KEY in production. The default values are only for development.
