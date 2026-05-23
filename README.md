# AI-Powered Security Monitoring & Intelligent Threat Detection Platform

Intelligent cybersecurity platform designed for high-velocity network log ingestion, real-time feature extraction, ensemble threat classification, and live security visualization.

## Architecture Highlights
- **Ingestion Layer:** Django REST Framework API backed by TimescaleDB for highly optimized time-series log writes.
- **Messaging Stream:** Apache Kafka buffer decoupling REST ingestion from pipeline operations.
- **Pipeline Layer:** Celery worker pools executing overlapping 5-minute sliding feature aggregates.
- **ML Engine (FastAPI):** Multi-model ensemble running unsupervised Isolation Forests, multi-class XGBoost classifiers, and temporal LSTM autoencoders.
- **Presentation:** Modern, responsive dark cybertheme React + Vite dashboard powered by Tailwind CSS, Recharts, and Channels WebSockets.
- **Edge AI:** Micro ARM MQTT log classifiers utilizing ONNX runtime pipelines.

## Project Structure
```
├── backend/                  # Django project, channels ASGI, celery workers
├── ml-service/               # FastAPI microservice for ML model serving
├── ml-training/              # Standalone scikit-learn, XGBoost, and PyTorch pipelines
├── pipeline/                 # Standalone streaming producers and consumer brokers
├── edge/                     # ARM / Raspberry Pi lightweight ONNX MQTT classifier
├── frontend/                 # React 18 + Vite + Tailwind CSS dashboard
└── docker-compose.yml        # Development environment stack
```

## Quick Start (Docker Development)

1. **Configure Environment:**
   ```bash
   cp .env.example .env
   ```

2. **Launch the Stack:**
   ```bash
   make up
   # or: docker compose up -d --build
   ```

3. **Initialize Database:**
   ```bash
   make migrate
   make superuser
   ```

4. **Run Ingestion Producer Simulation:**
   ```bash
   make edge-sim
   ```

5. **Access Interfaces:**
   - **Frontend Dashboard:** `http://localhost:3000`
   - **Backend API Docs:** `http://localhost:8000/api/docs/`
   - **ML Service Health:** `http://localhost:8001/health`
   - **MLflow Tracking:** `http://localhost:5000`
   - **Grafana Dashboard:** `http://localhost:3001` (Admin / admin_password_change_me)

## Model Training & Evaluation
To retrain models on synthetic baseline traffic, run:
```bash
make train
make evaluate
```
Benchmarked results, including confusion matrices and comparative metrics, are outputted under `docs/experiment-results/model_comparison.csv`.
