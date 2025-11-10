# OOF

A fraud detection system using Machine Learning (Isolation Forest) deployed as a scalable REST API with PostgreSQL and Redis caching.

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
| **Inference Time** | <50ms |

"Given the extreme class imbalance (0.17% fraud), I optimized the model for recall to catch as many fraud cases as possible, accepting the lower precision. The 95.3% ROC-AUC demonstrates strong discriminative ability, while the fast inference time (<50ms) makes the system practical for real-time deployment. The F1-score is low, but for fraud detection, maximizing recall has higher priority than a good F1-score. Also since  F1 = 2 × (precision × recall) / (precision + recall), the low precision (6.61%) mathematically constrains the F1-score.
## Problems I Faced

### 1. Choosing the Right Algorithm
Because the dataset had a lot of class imbalance, I chose Isolation Forest because it works very good in isolating outliers. 

### 2. Threshold Optimization
Setting the threshold too low = false alarms, too high = missed fraud. I created a script to test different thresholds and visualize the trade-off between recall and precision. Eventually found a sweet spot where 81% of frauds are caught while keeping the system practically feasible.

### 3. Feature Scaling
Time and Amount had different scales than V1-V28 features. Applied StandardScaler to normalize them, which significantly improved model accuracy.

## Tech Stack

- **Python 3.13**
- **FastAPI** 
- **scikit-learn** 
- **PostgreSQL** 
- **Redis** 
- **Docker**
- **SQLAlchemy** 
- **Alembic** 


### Run with Docker

Run the entire application stack with one command:

```bash
# Start all services (API, PostgreSQL, Redis)
docker-compose -f config/docker-compose.yml up -d

# Check status
docker ps

# View logs
docker logs fraud_detection_api

# Stop all services
docker-compose -f config/docker-compose.yml down
```

API will be available at `http://localhost:8000`

### Local Development Setup

For development with faster iteration:

```bash
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

# Start Redis (Docker)
docker run -d --name redis-fraud -p 6379:6379 redis:7

# Set up PostgreSQL (use local installation or Docker)

# Run database migrations
alembic upgrade head

# Start API
python start_api.py
# OR
uvicorn src.main:app --reload
```

**Deployment Approach:**
- Developed locally with hybrid setup (local Python + Docker Redis).
- Containerized entire stack for production deployment
- Docker Compose orchestrates all services with health checks

## License

This project is for educational purposes.
