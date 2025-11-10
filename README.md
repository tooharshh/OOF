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

### 1. Choosing the Right Algorithm
Because the dataset had a lot of class imbalance, I chose Isolation Forest because it works very good in isolating outliers. 

### 2. Threshold Optimization
Setting the threshold too low meant too many false alarms, too high meant missing real fraud. I created a script to test different thresholds and visualize the trade-off between recall and precision. Eventually found a sweet spot where we catch 81% of frauds while keeping the system practical.

### 3. Feature Scaling
The 'Time' and 'Amount' features had very different scales compared to the V1-V28 features. Initially, the model was giving too much weight to these unscaled features. I solved this by applying StandardScaler to normalize them before training, which improved model performance significantly.

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

![Fraud Detection Architecture](architecture.svg)

### Prerequisites

- Python 3.13.9
- Docker and Docker Compose
- PostgreSQL 13 (if running without Docker)
- Redis 6 (if running without Docker)
