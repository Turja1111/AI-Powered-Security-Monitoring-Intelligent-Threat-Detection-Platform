

AI-Powered Security Monitoring &
## Intelligent Threat Detection Platform
A Capstone Portfolio Project for EDISS — Erasmus Mundus Joint Master
Programme Engineering of Data-Intensive Intelligent Software Systems

Table of Contents
## 1. Project Overview
- Motivation & EDISS Alignment
## 3. System Architecture
## 4. Technology Stack
## 5. Project Structure
## 6. Database Design
## 7. Backend — Django Services
## 8. Data Pipeline Design
## 9. Machine Learning Engine
## 10. Alerting & Notification System
## 11. Frontend — Dashboard Design
- Edge AI Layer
- DevOps & Containerisation
- CI/CD Pipeline
## 15. Cloud Deployment
## 16. Research & Evaluation Plan
- Phase-by-Phase Build Plan
- GitHub Repository Standards
- CV & SOP Talking Points

## 1. Project Overview
## What This Project Is

A full-stack, distributed, AI-powered security monitoring platform that ingests network
logs and system events, processes them through an intelligent pipeline, detects
anomalies and intrusions using machine learning, and presents actionable threat
intelligence through a real-time dashboard.
This is not a simple ML notebook. It is a complete, production-grade intelligent software
system — from raw data ingestion to cloud deployment — built to demonstrate every
competency that EDISS evaluates.
## Problem Statement
Modern network infrastructure generates millions of log events per day. Manual analysis
is impossible at scale. Traditional rule-based intrusion detection systems (IDS) produce
excessive false positives and fail to detect novel attack patterns. There is a critical need
for an intelligent, adaptive, data-driven platform that can:
● Ingest high-velocity log data from multiple sources in real time
● Automatically detect anomalous behaviour using machine learning
● Prioritise alerts by severity to reduce analyst fatigue
● Scale horizontally across distributed infrastructure
● Operate at the network edge with constrained hardware
This platform solves exactly that problem.
What Makes It EDISS-Grade
EDISS Curriculum Course How This Project Covers It
Data Science Log feature extraction, statistical analysis, EDA
Machine Learning Isolation Forest, XGBoost, LSTM anomaly
detection
Software Architectures Microservices, layered architecture, REST API
design
Cloud Computing GCP Cloud Run, Docker, Kubernetes basics
Edge Computing for ML ONNX model on Raspberry Pi via MQTT
Data-Driven Computing
## Architectures
Apache Kafka, streaming pipelines
Software Verification & Validation pytest, integration tests, CI/CD

Research Methods Comparative ML study, benchmarks, mini-paper

- Motivation & EDISS Alignment
## Why This Problem Matters
Cybersecurity is one of the most data-intensive domains in existence. Every packet,
every login attempt, every DNS query is a data point. The challenge is not collecting
data — it is making sense of it intelligently, at speed, at scale. This platform represents
exactly the kind of real-world intelligent system that EDISS trains students to build.
Personal Motivation (SOP Context)
The intersection of software engineering, AI, and security is underexplored compared to
pure ML research. Most security tools are either brittle rule-based systems or black-box
commercial products. There is a gap for transparent, well-engineered, open-source
intelligent security systems. This project is an attempt to close that gap at a research
prototype level.
Connection to EDISS Research Areas
EDISS partner universities conduct active research in:
● Intelligent systems and autonomic computing (Åbo Akademi)
● Software quality and verification (University of L'Aquila)
● Computer vision and intelligent systems (UPM Madrid)
● Data-intensive architectures (University of Groningen)
This project touches all four research threads and prepares for meaningful contribution
to any of them.

## 3. System Architecture
High-Level Overview
The system follows a layered microservices architecture with a clear separation
between data ingestion, processing, intelligence, and presentation layers.

## ┌──────────────────────────────────────────────────────
## ───────┐
## │                      DATA SOURCES LAYER                     │
│  CICIDS2017 Dataset │ Synthetic Generator │ System Logs     │
│                     │ Edge Device (MQTT)  │                 │
## └──────────────────────────────┬───────────────────────
## ───────┘
## │
## ┌──────────────────────────────▼──────────────────────
## ────────┐
## │                     INGESTION LAYER                         │
│         Django REST API  ←→  Apache Kafka Topics            │
│         (Batch + Streaming ingestion endpoints)             │
## └──────────────────────────────┬───────────────────────
## ───────┘
## │
## ┌──────────────────────────────▼──────────────────────
## ────────┐
## │                      PIPELINE LAYER                         │
│    PostgreSQL (logs)  │  Redis (cache)  │  Feature Store    │
│    Kafka Consumer     │  ETL Workers    │  Celery Tasks      │
## └──────────────────────────────┬───────────────────────
## ───────┘
## │
## ┌──────────────────────────────▼──────────────────────
## ────────┐
## │                    ML INTELLIGENCE LAYER                    │
│   Isolation Forest  │  XGBoost Classifier  │  LSTM (Seq.)   │
│        Model Registry (MLflow) + Serving API                │
## └──────────────────────────────┬───────────────────────
## ───────┘
## │
## ┌──────────────────────────────▼──────────────────────
## ────────┐
## │                      OUTPUT LAYER                           │
## │   React Dashboard  │  Grafana  │  Alert Engine  │  Reports  │
## └──────────────────────────────────────────────────────
## ───────┘
All containerised via Docker Compose
Deployed to GCP Cloud Run + Cloud SQL


## Architectural Decisions & Rationale
Why Django over FastAPI? Django provides a complete web framework with ORM,
admin panel, authentication, and migration management out of the box. For a portfolio
project, Django's built-in admin interface also serves as a bonus monitoring tool. Django
REST Framework (DRF) provides a production-standard API layer. FastAPI is used only
for the lightweight ML serving microservice where async performance matters most.
Why Kafka over direct DB writes? Log data is high-velocity. Writing directly from the
ingestion API to PostgreSQL under load creates bottlenecks. Kafka acts as a durable
buffer — the API publishes to a topic instantly, and a separate consumer processes and
stores at its own pace. This decoupling is a hallmark of production data engineering.
Why separate ML service? Keeping ML inference in a separate FastAPI microservice
means models can be updated, scaled, and swapped without touching the main Django
application. This is standard MLOps practice and demonstrates software architecture
maturity.
Why Redis? Caching ML prediction results prevents redundant computation on
identical or near-identical feature vectors. Redis also manages rate limiting on the
ingestion API and stores real-time alert state for the dashboard without DB round-trips.

## 4. Technology Stack
## Backend
## Component Technology Justification
## Web
framework
Django 4.2 + Django REST
## Framework
Production-standard, ORM, admin,
migrations
ML serving FastAPI 0.104 Async, lightweight, perfect for
inference endpoints
Task queue Celery + Redis broker Async ETL jobs, scheduled retraining
## Message
broker
Apache Kafka (Confluent) High-throughput log streaming

Caching Redis 7 Alert state, prediction cache, rate
limiting
## Primary
database
PostgreSQL 15 Relational logs, alerts, user data
Time-series TimescaleDB extension on
PostgreSQL
Efficient time-series queries on log
data
## Machine Learning
## Component Technology Justification
Data processing Pandas, NumPy Industry standard for tabular
data
ML models Scikit-learn, XGBoost Isolation Forest + classifier
Deep learning PyTorch (LSTM) Sequence anomaly detection
## Experiment
tracking
MLflow Model versioning, metric
logging
Edge inference ONNX Runtime Cross-platform,
hardware-agnostic
Feature store Custom (PostgreSQL
table)
Reproducible feature
engineering
## Frontend
## Component Technology Justification
## Dashboard
framework
React 18 + Vite Component-based, fast dev
experience
UI component
library
shadcn/ui + Tailwind CSS Modern, accessible, easy to
customise
Charts & graphs Recharts + D3.js Flexible data visualisation
Real-time updates WebSockets (Django
## Channels)
Live alert feed without polling

## Monitoring
dashboards
Grafana (alongside React) Industry-standard ops
dashboards
DevOps & Infrastructure
## Component Technology Justification
## Containerisation Docker + Docker
## Compose
One-command local setup
## Orchestration
## (basic)
Kubernetes (GKE,
## Phase 3)
Demonstrates cloud-native thinking
CI/CD GitHub Actions Automated test, lint, build, deploy
Cloud platform Google Cloud
## Platform
Cloud Run (serverless), Cloud SQL,
## Artifact Registry
Infrastructure as
## Code
Terraform (basic) Reproducible cloud infrastructure
## Monitoring Prometheus +
## Grafana
Service health, latency, throughput
## Data & Datasets
## Dataset Source Purpose
CICIDS2017 University of New
## Brunswick
Primary labelled network intrusion
dataset
NSL-KDD UNB / Kaggle Secondary benchmark for comparison
UNSW-NB15 UNSW Canberra Modern attack variety, research
comparison
## Synthetic
generator
Custom Python script Continuous stream simulation

## 5. Project Structure
security-monitoring-platform/
## │

├── README.md                          # Project overview, setup, demo link
├── docker-compose.yml                 # Full local stack
├── docker-compose.prod.yml            # Production overrides
├── .env.example                       # Environment variable template
├── Makefile                           # Shortcut commands
## │
├── backend/                           # Django application
│   ├── manage.py
│   ├── requirements.txt
## │   ├── Dockerfile
│   ├── config/                        # Django settings
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── ingestion/                 # Log ingestion app
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests/
│   │   ├── pipeline/                  # ETL + Kafka consumer app
│   │   │   ├── consumers.py
│   │   │   ├── tasks.py               # Celery tasks
│   │   │   ├── feature_engineering.py
│   │   │   └── tests/
│   │   ├── alerts/                    # Alert management app
│   │   │   ├── models.py
│   │   │   ├── engine.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── tests/
│   │   └── dashboard/                 # WebSocket + API for frontend
│   │       ├── consumers.py           # Django Channels WebSocket
│   │       ├── views.py
│   │       └── routing.py
│   └── core/

│       ├── cache.py                   # Redis abstraction
│       ├── pagination.py
│       └── permissions.py
## │
├── ml-service/                        # FastAPI ML inference microservice
│   ├── main.py
│   ├── requirements.txt
## │   ├── Dockerfile
│   ├── models/
│   │   ├── isolation_forest.py
│   │   ├── xgboost_classifier.py
│   │   └── lstm_detector.py
│   ├── serving/
│   │   ├── predictor.py
│   │   └── preprocessor.py
│   └── tests/
## │
├── ml-training/                       # Training scripts (not served)
│   ├── notebooks/
## │   │   ├── 01_exploratory_analysis.ipynb
## │   │   ├── 02_feature_engineering.ipynb
## │   │   ├── 03_model_training.ipynb
## │   │   └── 04_evaluation_comparison.ipynb
│   ├── train_isolation_forest.py
│   ├── train_xgboost.py
│   ├── train_lstm.py
│   ├── evaluate.py
│   └── mlflow_tracking.py
## │
├── pipeline/                          # Kafka producer/consumer scripts
│   ├── producer.py                    # Log source simulator
│   ├── consumer.py                    # Reads from Kafka, feeds ML
│   └── feature_store.py
## │
├── edge/                              # Raspberry Pi edge AI code
│   ├── mqtt_publisher.py
│   ├── onnx_inference.py
│   └── edge_config.yaml
## │
├── frontend/                          # React dashboard

│   ├── package.json
│   ├── vite.config.ts
## │   ├── Dockerfile
│   ├── src/
## │   │   ├── App.tsx
│   │   ├── components/
## │   │   │   ├── Dashboard/
│   │   │   ├── AlertFeed/
│   │   │   ├── ThreatMap/
│   │   │   ├── ModelMetrics/
│   │   │   └── LogViewer/
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useAlerts.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
## │
├── grafana/                           # Grafana dashboard configs
│   ├── dashboards/
│   │   ├── overview.json
│   │   ├── alert-timeline.json
│   │   └── model-performance.json
│   └── provisioning/
## │
├── infrastructure/                    # Terraform + K8s manifests
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── gcp.tf
│   └── k8s/
│       ├── backend-deployment.yaml
│       ├── ml-service-deployment.yaml
│       └── ingress.yaml
## │
├── docs/                              # Research & documentation
│   ├── architecture.png
│   ├── research-report.pdf            # 4-page mini-paper
│   ├── api-reference.md

│   └── experiment-results/
│       ├── model_comparison.csv
│       └── benchmark_charts/
## │
## └── .github/
└── workflows/
├── ci.yml                     # Test + lint on every PR
└── deploy.yml                 # Deploy on merge to main


## 6. Database Design
## Core Tables
logs — raw ingested events
id                  UUID PRIMARY KEY
timestamp           TIMESTAMPTZ NOT NULL
source_ip           INET
destination_ip      INET
source_port         INTEGER
destination_port    INTEGER
protocol            VARCHAR(10)        -- TCP, UDP, ICMP
bytes_sent          BIGINT
bytes_received      BIGINT
duration_ms         INTEGER
packet_count        INTEGER
tcp_flags           VARCHAR(20)
label               VARCHAR(50)        -- normal / attack type (if known)
source              VARCHAR(50)        -- dataset name or 'live'
ingested_at         TIMESTAMPTZ DEFAULT NOW()

features — engineered feature vectors per log window
id                  UUID PRIMARY KEY
window_start        TIMESTAMPTZ
window_end          TIMESTAMPTZ
source_ip           INET
feature_vector      JSONB              -- normalised feature array

anomaly_score       FLOAT              -- Isolation Forest output
predicted_label     VARCHAR(50)        -- XGBoost output
confidence          FLOAT
computed_at         TIMESTAMPTZ DEFAULT NOW()

alerts — generated security alerts
id                  UUID PRIMARY KEY
created_at          TIMESTAMPTZ DEFAULT NOW()
severity            VARCHAR(20)        -- LOW / MEDIUM / HIGH / CRITICAL
alert_type          VARCHAR(100)       -- port_scan / brute_force / exfiltration / etc
source_ip           INET
destination_ip      INET
anomaly_score       FLOAT
model_used          VARCHAR(50)
description         TEXT
status              VARCHAR(20)        -- OPEN / ACKNOWLEDGED / RESOLVED
acknowledged_by     VARCHAR(100)
resolved_at         TIMESTAMPTZ
raw_log_ids         UUID[]             -- FK array to logs table

model_registry — trained model metadata
id                  UUID PRIMARY KEY
model_name          VARCHAR(100)
version             VARCHAR(20)
algorithm           VARCHAR(50)
dataset_trained_on  VARCHAR(100)
f1_score            FLOAT
precision_score     FLOAT
recall_score        FLOAT
roc_auc             FLOAT
training_date       TIMESTAMPTZ
is_active           BOOLEAN DEFAULT FALSE
mlflow_run_id       VARCHAR(100)
artifact_path       TEXT

pipeline_runs — ETL job audit trail

id                  UUID PRIMARY KEY
started_at          TIMESTAMPTZ
completed_at        TIMESTAMPTZ
records_processed   INTEGER
records_failed      INTEGER
status              VARCHAR(20)
error_message       TEXT

## Indexing Strategy
● logs(timestamp) — B-tree index for time-range queries
● logs(source_ip, timestamp) — composite for per-IP queries
● alerts(severity, created_at) — dashboard filtering
● alerts(status) — open alert queue
● features(window_start) — time-series feature lookups
TimescaleDB hypertable on logs(timestamp) enables automatic time-based
partitioning, dramatically improving query performance on large datasets.

## 7. Backend — Django Services
## Django App Breakdown
ingestion app — handles all incoming log data
## Responsibilities:
● REST endpoints for batch CSV upload and single-event POST
● Input validation and sanitisation via DRF serializers
● Publishes raw events to Kafka topic raw-logs
● API key authentication for programmatic access
● Rate limiting via Redis (100 requests/minute per key)
Key endpoints:
POST   /api/v1/logs/batch/        Upload CSV file, returns job_id
POST   /api/v1/logs/event/        Single log event
GET    /api/v1/logs/              Paginated log list with filters

GET    /api/v1/logs/{id}/         Single log detail
GET    /api/v1/logs/stats/        Aggregated statistics

pipeline app — ETL and feature engineering
## Responsibilities:
● Kafka consumer that reads from raw-logs topic
● Celery tasks for batch feature engineering
● Feature normalisation, encoding, windowing
● Writes processed features to features table
● Scheduled retraining trigger (weekly Celery beat job)
alerts app — alert management and lifecycle
## Responsibilities:
● Receives scored events from ML service
● Applies severity classification rules
● Deduplicates repeated alerts (Redis-based)
● Manages alert lifecycle (open → acknowledged → resolved)
● Sends webhook notifications to Slack or email
● Exposes alert API for the React dashboard
Key endpoints:
GET    /api/v1/alerts/            Paginated alert list with severity filter
GET    /api/v1/alerts/{id}/       Alert detail with raw log context
PATCH  /api/v1/alerts/{id}/       Update status (acknowledge/resolve)
GET    /api/v1/alerts/summary/    Count by severity for dashboard cards

dashboard app — WebSocket and aggregation API
## Responsibilities:
● Django Channels WebSocket consumer for real-time alert push
● Aggregation endpoints for chart data
● Serves time-series data for Recharts visualisations
Django REST Framework Design Principles

● ViewSets with Routers for standard CRUD
● Custom pagination (cursor-based for log streams)
● Permission classes: IsAuthenticated for dashboard, HasAPIKey for
ingestion
● Throttling: separate rates for ingestion vs dashboard
● Custom exception handler returning consistent error schema
● OpenAPI schema auto-generated via drf-spectacular

## 8. Data Pipeline Design
## Flow Overview
## Log Source
## │
## ▼
Django Ingestion API  ──────────────────────────────────►
PostgreSQL (raw logs)
## │
## ▼
Kafka Topic: raw-logs
## │
## ▼
Kafka Consumer (Python)
## │
## ├── Feature Engineering Worker
## │       │
## │       ▼
│   Features Table (PostgreSQL)
## │       │
## │       ▼
│   ML Service (FastAPI) ──► Prediction + Score
## │       │
## │       ▼
│   Kafka Topic: scored-events
## │
## ▼
Alert Engine (Celery Task)
## │
## ▼

Alerts Table ──► WebSocket Push ──► React Dashboard

## Kafka Topics
## Topic Producer Consumer Retentio
n
raw-logs
Django API Pipeline consumer 24 hours
scored-ev
ents
ML service Alert engine 12 hours
alerts
## Alert
engine
WebSocket /
webhook
7 days
edge-even
ts
## Raspberry
## Pi
Pipeline consumer 24 hours
## Feature Engineering Pipeline
The feature engineering step transforms raw log records into numerical vectors suitable
for ML models. This runs as a sliding window aggregation over 5-minute and 15-minute
buckets.
Features extracted per window per source IP:
Volume features
● Total bytes sent and received
● Packet count, average packet size
● Connection count, unique destination IPs
● Unique destination ports
Behavioural features
● Protocol distribution (TCP/UDP/ICMP ratio)
● Top destination port entropy (high entropy = scanning)
● Average connection duration
● Bytes per packet ratio
Temporal features

● Requests per second
● Inter-arrival time mean and standard deviation
● Night-time activity flag (00:00–06:00)
Derived features
● Bytes sent / bytes received ratio (asymmetry = exfiltration signal)
● Distinct port count in window (high = port scan)
● Failed connection ratio (high = brute force signal)
All features are normalised with StandardScaler fitted on a baseline normal-traffic
window. Categorical fields (protocol) are one-hot encoded. The fitted scaler is saved
alongside each model version in MLflow.
## Celery Task Design
## Task Schedule Purpose
process_feature_
window
## Every 5
minutes
Aggregate features from last
window
run_batch_infere
nce
## Every 5
minutes
Score unscored feature rows
trigger_alert_en
gine
## Every 5
minutes
Evaluate scored events for alerts
retrain_models
Weekly Retrain on latest labelled data
cleanup_old_logs
Daily Archive logs older than 90 days
generate_daily_r
eport
Daily 08:00 Summary PDF for dashboard

## 9. Machine Learning Engine
Model 1 — Isolation Forest (Unsupervised)
What it does: Detects anomalies without requiring labelled data. Builds an ensemble of
isolation trees; events that require fewer splits to isolate are flagged as anomalies.

Why it is ideal here: Real-world security data often lacks reliable labels. Isolation
Forest operates on unlabelled normal traffic, making it deployable in new environments
immediately.
Training approach:
● Train on a clean baseline of normal traffic (first 20% of dataset, normal-labelled
records only)
● contamination parameter set to 0.05 (expect ~5% anomalies)
● n_estimators = 200 for stability
● Output: anomaly score between -1 (anomaly) and 1 (normal)
Threshold tuning: Score threshold is calibrated on a validation set to balance precision
and recall. Threshold stored in model registry alongside the model artifact.
Model 2 — XGBoost Classifier (Supervised)
What it does: Gradient-boosted decision tree classifier trained on the labelled
CICIDS2017 dataset. Predicts attack type across 15 classes including DDoS, port scan,
brute force, web attacks, and infiltration.
Why it is used here: XGBoost consistently outperforms other algorithms on tabular
network security data. Its interpretability via feature importance is valuable for security
analysts.
Training approach:
● Multi-class classification (15 attack classes + normal)
● Class weights balanced to handle imbalanced labels
● Hyperparameter tuning via Optuna (100 trials)
● Key hyperparameters: max_depth, learning_rate, n_estimators,
subsample
● SHAP values computed for every prediction (explainability)
Evaluation metrics:
● Per-class precision, recall, F1
● Macro and weighted averages
● Confusion matrix
● ROC-AUC (one-vs-rest for multi-class)
Model 3 — LSTM (Sequence-Based, Phase 3)

What it does: Learns temporal patterns in log sequences per source IP. Flags source
IPs whose behaviour deviates from their own learned baseline over time.
Why it is valuable: Isolation Forest and XGBoost evaluate each window independently.
LSTM captures slow-burn attacks that unfold gradually over hours — reconnaissance,
lateral movement — which look normal in any single window.
Training approach:
● Input: sequence of 20 consecutive 5-minute feature windows per source IP
● Architecture: 2-layer LSTM → Dense → sigmoid output
● Trained as an autoencoder: reconstruction error = anomaly score
● Source IPs with high average reconstruction error over 24 hours are flagged
ML Serving (FastAPI Microservice)
The ML service exposes a clean prediction API consumed by the Django pipeline:
POST   /predict/isolation-forest    Returns anomaly score for feature vector
POST   /predict/xgboost             Returns predicted label + confidence + SHAP values
POST   /predict/lstm                Returns sequence reconstruction error
GET    /models/active               Lists currently active model versions
GET    /health                      Service health check

Model loading uses MLflow model registry. The active model version is loaded at startup
and cached in memory. Model hot-swap (switching versions without restart) is supported
via a reload endpoint.
MLflow Experiment Tracking
Every training run logs:
● Dataset name and version
● Hyperparameters (full dict)
● Training metrics (loss curves for LSTM, CV scores for others)
● Evaluation metrics (precision, recall, F1, ROC-AUC)
● Confusion matrix as artifact
● Fitted scaler and model artifact
● Feature importance plot (XGBoost)
● Git commit hash

This creates a full audit trail of every model version — demonstrating research-grade
rigor that EDISS evaluators recognise immediately.

## 10. Alerting & Notification System
## Severity Classification
Alerts are classified into four severity levels based on model output and rule logic:
## Severity Criteria Response
## Time
CRITICAL Isolation Forest score < -0.7 AND XGBoost confidence
> 0.95 for DDoS/exfiltration
## Immediate
webhook
HIGH XGBoost confidence > 0.85 for known attack class Within 5
minutes
MEDIUM Isolation Forest score < -0.4 OR XGBoost confidence >
## 0.60
Within 1 hour
LOW Isolation Forest score < -0.2 (borderline anomaly) Dashboard
review
## Deduplication Logic
A Redis-based deduplication mechanism prevents alert floods. When an alert is
generated:
- A deduplication key is constructed:
alert:{source_ip}:{alert_type}:{severity}
- Redis checks if this key exists (TTL: 15 minutes for HIGH, 60 minutes for
## MEDIUM/LOW)
- If the key exists, the alert is suppressed and the existing alert's count is
incremented
- If the key is new, the alert is created and the key is set with appropriate TTL
This mimics the deduplication logic used in production SIEM systems.
## Notification Channels

Slack webhook — CRITICAL and HIGH alerts sent to a configurable Slack channel
with formatted message including source IP, attack type, confidence, and link to alert
detail.
Email — Daily digest email summarising alert counts by severity, top attacking IPs, and
model performance metrics.
WebSocket push — All alerts are pushed in real time to connected React dashboard
clients via Django Channels, without polling.

## 11. Frontend — Dashboard Design
## Technology Choice
React 18 with Vite build tool. Tailwind CSS for styling. shadcn/ui for accessible
component primitives. Recharts for data visualisation. WebSocket hook for real-time
updates.
## Pages & Components
Overview Dashboard (/) — the landing page
## Components:
● 4 metric cards: total alerts today, critical count, logs ingested, active model
accuracy
● Real-time alert ticker (WebSocket feed, last 20 alerts)
● Time-series chart: alert volume over last 24 hours (Recharts LineChart)
● Severity distribution donut chart (last 7 days)
● Top 10 attacking source IPs table
Alert Management (/alerts) — alert investigation
## Components:
● Filterable, sortable alert table (severity, type, status, time range)
● Alert detail drawer: full context, raw logs, SHAP values, recommended action
● Bulk acknowledge / resolve actions
● Alert timeline chart
Log Explorer (/logs) — raw data exploration

## Components:
● Virtualized log table (handles 100k+ rows without lag)
● Filter bar: IP, port, protocol, time range, label
● Inline anomaly score column (colour-coded)
● Export to CSV button
ML Models (/models) — model performance monitoring
## Components:
● Active model cards with F1, precision, recall badges
● Confusion matrix heatmap (D3.js)
● ROC curve chart per model
● Feature importance bar chart (XGBoost SHAP)
● Model version history table from MLflow
Edge Devices (/edge) — edge node monitoring
## Components:
● Connected device list with last-seen timestamp
● Per-device event rate sparkline
● Edge vs cloud latency comparison chart
Real-Time Architecture
Django Channels handles WebSocket connections. When the alert engine creates a
new alert, it publishes to a Redis channel group. Django Channels broadcasts to all
connected WebSocket clients. The React
useWebSocket hook receives the event and
updates the alert feed state without a page refresh or polling.
This is the kind of real-time systems thinking that demonstrates genuine software
engineering maturity.

- Edge AI Layer
## Purpose
Deploy a lightweight version of the trained XGBoost model on a resource-constrained
device (Raspberry Pi 4 or equivalent). The edge device processes logs locally, runs

inference, and publishes only alert-worthy events to the cloud via MQTT. This reduces
bandwidth, latency, and cloud compute costs — demonstrating understanding of edge
computing tradeoffs.
## Model Conversion
The XGBoost model is exported to ONNX format using sklearn-onnx. ONNX
Runtime is available on ARM (Raspberry Pi) and requires no Python ML dependencies
at inference time, keeping the edge footprint small.
Data Flow on Edge
Local sensor / log file
## │
## ▼
Feature engineering script (Python, runs on Pi)
## │
## ▼
ONNX Runtime inference
## │
## ┌───┴────────────┐
│ Normal event   │ Anomaly detected
│ — discarded    │
## └────────────────┘
## │
## ▼
MQTT publish to broker
## │
## ▼
Cloud Kafka consumer
## │
## ▼
Alert engine (same as cloud path)

## Benchmark Study
As part of the research layer, a benchmarking study compares:
● Inference latency: edge (ONNX on Pi) vs cloud (FastAPI on Cloud Run)
● Bandwidth: full log upload vs edge-filtered alert upload
● Accuracy: edge ONNX model vs cloud full model (quantisation impact)

● Cost model: estimated GCP compute cost with and without edge filtering
This benchmark is documented in the research report and gives the project a genuine
systems research dimension.

- DevOps & Containerisation
## Docker Compose Services
The full local stack runs with a single command: docker compose up --build
## Service Image Purpose
backend
Custom Django REST API, WebSocket,
## Celery
celery-wo
rker
Same Django image Background task processing
celery-be
at
Same Django image Scheduled task scheduler
ml-servic
e
Custom FastAPI Model serving
db
postgres:15-alpine Primary database
cache
redis:7-alpine Caching and message
broker
kafka
confluentinc/cp-kafka Log streaming
zookeeper
confluentinc/cp-zookee
per
Kafka coordination
grafana
grafana/grafana Ops dashboards
prometheu
s
prom/prometheus Metrics collection

frontend
## Custom React + Nginx Dashboard (production
build)
mlflow
Custom MLflow Experiment tracking UI
## Environment Configuration
All secrets and configuration live in .env (never committed to Git). An .env.example
file documents every required variable with descriptions. This is a professional practice
that shows awareness of security and deployment hygiene.
Multi-Stage Docker Builds
Both the Django and ML service Dockerfiles use multi-stage builds:
● Stage 1 (builder): installs all dependencies including build tools
● Stage 2 (runtime): copies only installed packages, no build tools
This reduces final image sizes significantly and is a production best practice.
## Health Checks
Every service in docker-compose.yml has a health check defined. The Django
backend depends on the db service being healthy (verified via pg_isready) before
starting. This prevents race condition errors on cold start.

- CI/CD Pipeline
GitHub Actions Workflows
ci.yml — runs on every push and pull request
## Steps:
- Checkout code
- Set up Python 3.11
- Install dependencies
- Run black formatter check
- Run flake8 linting

- Run isort import order check
- Run pytest with coverage report
- Fail if coverage below 80%
- Build Docker images (validates Dockerfiles)
- Post coverage badge to README
deploy.yml — runs on merge to main
## Steps:
- Authenticate to GCP with Workload Identity Federation
- Build and push Docker images to GCP Artifact Registry
- Run database migrations via Cloud Run job
- Deploy backend to Cloud Run (zero-downtime rolling update)
- Deploy ml-service to Cloud Run
- Deploy frontend static build to Cloud Storage + CDN
- Run smoke tests against production URL
- Notify Slack channel on success or failure
## Branch Strategy
● main — protected, requires passing CI and one review
● develop — integration branch, deploys to staging
● feature/* — individual feature branches
● hotfix/* — emergency production fixes
This mirrors professional software team practices and demonstrates awareness of
software engineering workflows.

## 15. Cloud Deployment
GCP Services Used
## Service Purpose Estimated Monthly Cost
Cloud Run (backend) Django API, auto-scales to zero Free tier: 2M
requests/month

Cloud Run (ml-service) FastAPI inference, auto-scales Free tier: 2M
requests/month
Cloud SQL
(PostgreSQL)
Managed database ~$7/month (db-f1-micro)
Cloud Storage Frontend static files, model
artifacts
## ~$0.02/GB
Artifact Registry Docker images ~$0.10/GB
Cloud CDN Frontend asset delivery ~$0.01/GB
Secret Manager Environment secrets Free tier: 6 active secrets
Total estimated cost: under $15/month — keeping the project live on a student
budget.
## Deployment Architecture
## User Browser
## │
## ▼
Cloud CDN ──► Cloud Storage (React build, static files)
## │
## ▼
Cloud Run (Django backend) ──► Cloud SQL (PostgreSQL)
│                    └──► Redis (Memorystore or Cloud Run sidecar)
## ▼
Cloud Run (ML service) ──► Cloud Storage (model artifacts)
## │
## ▼
Kafka (self-hosted on GCP VM, or Confluent Cloud free tier)

Why Cloud Run Over App Engine or GKE
Cloud Run is the right choice for a portfolio project:
● No cluster management overhead (unlike GKE)
● Auto-scales to zero when not in use (zero cost when idle)
● Container-native (same Docker image as local)
● Free tier covers typical portfolio traffic easily

Kubernetes manifests are still written and included in infrastructure/k8s/ to
demonstrate knowledge of orchestration — they just are not the primary deployment
method.

## 16. Research & Evaluation Plan
## Experiment Design
The research layer transforms this from a software project into a scientific contribution.
Three experiments are conducted and documented in a 4-page mini-paper format.
## Experiment 1 — Model Comparison Study
Research question: Which anomaly detection algorithm achieves the best F1 score on
network intrusion data while maintaining real-time inference speed?
## Method:
● Three models: Isolation Forest, XGBoost, LSTM
● Three datasets: CICIDS2017, NSL-KDD, UNSW-NB15
● Five metrics per combination: precision, recall, F1, ROC-AUC, inference latency
## (ms)
● 5-fold cross-validation on each dataset
● Results reported as mean ± standard deviation
Expected outcome: XGBoost highest F1 on labelled data; Isolation Forest better on
novel attacks; LSTM best on slow-burn sequential attacks.
Experiment 2 — Edge vs Cloud Tradeoff
Research question: What is the accuracy-latency-bandwidth tradeoff when deploying
ONNX-quantised models at the edge versus full models in the cloud?
## Method:
● Measure inference latency at edge (Raspberry Pi 4) vs cloud (Cloud Run, 1
vCPU)
● Measure bandwidth usage: full log upload vs edge-filtered alert upload
● Compare F1 scores: ONNX quantised vs original float32 XGBoost
● Vary network conditions (simulated 50ms, 100ms, 500ms latency)

## Experiment 3 — Alert Deduplication Effectiveness
Research question: How does the Redis-based deduplication mechanism affect alert
volume and mean time to detection?
## Method:
● Replay CICIDS2017 attack scenarios with and without deduplication
● Measure: alert count reduction, false negative rate introduced by deduplication,
analyst workload proxy (alerts per hour)
● Vary deduplication TTL from 5 to 60 minutes
## Research Report Structure
- Abstract (150 words)
- Introduction — problem context, research questions
- Related Work — 5–8 cited papers on ML-based IDS
- System Design — brief architecture summary
- Experimental Setup — datasets, hardware, metrics
- Results — tables, ROC curves, confusion matrices
- Discussion — findings, limitations, future work
## 8. Conclusion
## References

This document lives at docs/research-report.pdf and is linked prominently in the
## README.
Metrics to Report in CV and SOP
After running experiments, fill in these slots with real numbers:
● XGBoost F1 score on CICIDS2017: [your result]
● Isolation Forest false positive rate: [your result]
● End-to-end pipeline latency (Kafka → alert): [your result] ms
● Edge inference latency (ONNX on Pi): [your result] ms
● Cloud inference latency: [your result] ms
● Bandwidth reduction with edge filtering: [your result] %
● Test coverage: [your result] %


- Phase-by-Phase Build Plan
Phase 1 — Foundation (Weeks 1–6)
Goal: Working ingestion + rule-based dashboard. Something you can demo.
Week 1–2: Environment & data
● Set up GitHub repository with proper .gitignore, README.md skeleton,
branch protection
● Download CICIDS2017 from UNB and explore in Jupyter notebook
● Write Python synthetic log generator (configurable attack rate, 1000 events/min)
● Initialise Django project with config/settings/ split
● Write initial PostgreSQL schema and Django models for logs and alerts
● Spin up PostgreSQL and Redis with basic docker-compose.yml
Week 3–4: Django ingestion API
● Build ingestion Django app with DRF
● Implement batch CSV upload endpoint with Celery async task
● Implement single-event POST endpoint
● Add API key authentication and rate limiting
● Write unit tests for all endpoints (target: 90% coverage on this app)
● Test CICIDS2017 ingestion end-to-end
Week 5–6: Dashboard + CI/CD skeleton
● Build basic React dashboard: log table, count cards, simple bar chart
● Add Django Channels for WebSocket connection (even if no real-time data yet)
● Set up GitHub Actions CI: lint, test, Docker build
● Write architecture diagram for README
● Verify docker compose up --build works from a clean checkout
● Tag v0.1.0 on GitHub — first shareable milestone
Phase 2 — ML Integration (Weeks 7–14)
Goal: Real-time anomaly detection with Kafka streaming.
Week 7–8: Feature engineering
● Write feature engineering module: sliding window aggregations
● Extract 20 features from CICIDS2017 logs

● Fit StandardScaler on normal traffic baseline
● Store feature vectors in features table
● Exploratory analysis notebook: distributions, attack class breakdown, feature
correlations
Week 9–10: ML models
● Train Isolation Forest on normal traffic subset
● Train XGBoost on full labelled CICIDS2017
● Evaluate both with sklearn metrics
● Set up MLflow tracking server (runs in Docker)
● Log all experiments with hyperparameters, metrics, artifacts
● Write comparison summary — this is the seed of the research report
Week 11–12: Kafka streaming
● Add Kafka and Zookeeper to Docker Compose
● Create topics: raw-logs, scored-events, alerts
● Modify Django ingestion to publish to Kafka instead of direct DB write
● Write Kafka consumer that reads raw-logs, runs feature engineering, calls ML
service
● Test end-to-end latency — log the numbers
Week 13–14: Alert engine + Grafana
● Build alert severity classification in Django alerts app
● Implement Redis-based deduplication
● Add Slack webhook notification
● Replace simple React charts with Grafana dashboards via PostgreSQL data
source
● Add real-time alert feed via Django Channels WebSocket to React dashboard
● Write integration tests for the full pipeline
● Tag v0.2.0 — demo-ready milestone
Phase 3 — Production + Research (Weeks 15–24)
Goal: Cloud deployment, edge AI, and research report.
Week 15–17: Cloud deployment
● Write Terraform for GCP infrastructure (Cloud Run, Cloud SQL, Artifact Registry)
● Push Docker images to GCP Artifact Registry

● Deploy Django backend and ML service to Cloud Run
● Set up GitHub Actions deploy workflow
● Verify live URL works end-to-end
● Add production environment settings (DEBUG=False, HTTPS,
## ALLOWED_HOSTS)
Week 18–19: Edge AI
● Export XGBoost to ONNX
● Write edge inference script for Raspberry Pi
● Write MQTT publisher (or simulate with Docker container)
● Run latency benchmark: edge vs cloud
● Run accuracy benchmark: ONNX vs original model
● Document edge architecture and add to README
Week 20–22: Research report
● Formalise experiments 1, 2, and 3 with proper methodology
● Run all experiments with 5-fold cross-validation
● Write results tables and generate charts
● Draft 4-page mini-paper in Overleaf or LaTeX
● Export as PDF, commit to docs/research-report.pdf
● Update README with link to paper and key results
Week 23–24: Polish + application prep
● Polish README: add badges, live demo GIF, architecture diagram, paper link
● Record 2-minute demo video: upload to YouTube (unlisted) and link from
## README
● Write CV bullet point with specific metrics
● Draft SOP paragraph referencing EDISS courses by name
● Final peer review: can a stranger understand the project in 60 seconds?
● Tag v1.0.0 — application-ready

- GitHub Repository Standards
README Structure
# AI Security Monitoring Platform
[2-line description]


[Demo GIF or screenshot]

[Live demo link] [Research paper link] [Build status badge] [Coverage badge]

## What it does
[3 bullet points, plain language]

## ## Architecture
[Architecture diagram image]

## Quick start
[3 commands to get it running locally]

## Tech stack
[Compact table]

## ## Research
[1-paragraph summary of findings, link to PDF]

## Project structure
[Tree, collapsed to top level]

## API reference
[Link to auto-generated docs at /api/docs/]

## ## Results
[Key metrics table]

## Commit Message Standard
Follow Conventional Commits format:
● feat: add XGBoost classifier to ML service
● fix: resolve Kafka consumer race condition
● docs: add experiment results to research report
● test: add integration tests for alert deduplication
● chore: update Docker base images

This signals professional development practice to anyone reading the commit history.
What Reviewers Look For in a GitHub Repo
● Can they run it in under 5 minutes? (One-command setup)
● Is there a live demo they can click to? (Public URL)
● Is the code readable without explanation? (Good naming, small functions)
● Is there evidence of testing? (Test directory, coverage badge)
● Is there a paper or report? (docs/research-report.pdf)
● Does the README answer every question before they have to ask?
(Architecture diagram, dataset source, setup steps, results)

- CV & SOP Talking Points
CV Bullet Point Template
AI Security Monitoring Platform | Python · Django · Apache Kafka · XGBoost ·
Docker · GCP | github.com/[yourname]/security-monitor

Built a distributed intelligent system for real-time network intrusion detection:
ingests logs via Apache Kafka (1000+ events/sec), detects anomalies using
Isolation Forest + XGBoost (F1: [X] on CICIDS2017), containerised with Docker
Compose, deployed to GCP Cloud Run with CI/CD via GitHub Actions. Edge inference
on Raspberry Pi via ONNX reduced bandwidth by [X]%. Includes 4-page research
report comparing 3 ML algorithms across 3 datasets.

SOP Paragraph Template
My portfolio project — an AI-powered security monitoring platform — directly
reflects what I hope to contribute to and learn from EDISS. The system addresses
a genuine engineering challenge: transforming high-velocity log data into
actionable threat intelligence through a complete stack of data pipelines,
machine learning, and distributed software architecture. Building it required
me to make and justify real architectural decisions — choosing Kafka over direct
writes for decoupling, selecting Isolation Forest for unlabelled environments
and XGBoost for supervised classification, and designing a Redis deduplication
layer to reduce analyst fatigue. The edge AI component, deploying ONNX models
to constrained hardware via MQTT, is what I look forward to extending in the
Edge Computing for ML course. The research report comparing three algorithms

across three benchmark datasets is my first attempt at scientific writing, and
I hope to deepen that skill in EDISS's research methodology courses.

## Motivation Video Checklist
● Name a specific EDISS course and explain how your project connects to it
● Mention a specific partner university's research group that aligns with your
interests
● Reference a specific technical challenge you solved and what you learned
● State your research question clearly — what do you still want to find out?
● Keep it under 3 minutes, speak clearly, good lighting
## Final Note
The strongest message you can send to any EDISS selection committee is not "I know
TensorFlow." It is: "I engineer complete intelligent systems from raw data to
deployed, tested, monitored production services — and I have a research mindset
about the tradeoffs."
This project, built fully and documented well, says exactly that.

Documentation version 1.0 — aligned with EDISS 2026 application cycle Project
repository: github.com/[yourname]/security-monitoring-platform
