# REST and WebSocket API Reference

This document outlines the API endpoints, WebSocket channels, and authentication protocols for the SecureWatch Platform.

## Authentication

All REST endpoints under `/api/v1/` and the FastAPI ML Service require an API Key.

* **Header Name:** `X-API-Key`
* **Example:** `X-API-Key: secure-api-key-here`

---

## Django Backend API (`/api/v1/`)

### Ingestion API

#### 1. POST `/api/v1/logs/event/`
Ingest a single network log event.
* **Payload Schema:**
```json
{
  "timestamp": "2026-05-23T10:00:00Z",
  "source_ip": "192.168.1.50",
  "destination_ip": "10.0.0.1",
  "source_port": 49200,
  "destination_port": 80,
  "protocol": "TCP",
  "bytes_sent": 12500,
  "bytes_received": 45000,
  "duration_ms": 250,
  "packet_count": 45,
  "tcp_flags": "SYN ACK",
  "label": "BENIGN",
  "source": "live"
}
```
* **Response (201 Created):**
```json
{
  "id": "a9ef387b-cdd8-48b4-9c9a-42823a2d2fb4",
  "timestamp": "2026-05-23T10:00:00Z",
  ...
}
```

#### 2. POST `/api/v1/logs/upload/`
Upload a CSV file of logs for batch processing.
* **Content-Type:** `multipart/form-data`
* **Form Parameters:**
  * `file`: (Binary CSV File)
  * `source`: (String, e.g. "cicids-2017")
* **Response (201 Created):**
```json
{
  "job_id": "b0f7d54b-d72b-42fa-9a5c-c76a9134a41d",
  "filename": "logs.csv",
  "status": "PROCESSING",
  "total_records": 50000
}
```

#### 3. GET `/api/v1/logs/stats/`
Retrieve general statistical aggregates for dashboard indicators.

---

### Alerts API

#### 1. GET `/api/v1/alerts/`
Query real-time security alerts. Supports filtering on `severity`, `status`, `alert_type`, and date ranges via `start_time` and `end_time`.

#### 2. PATCH `/api/v1/alerts/{id}/`
Update alert status (e.g., Acknowledge or Resolve).
* **Payload:**
```json
{
  "status": "ACKNOWLEDGED",
  "acknowledged_by": "operator_admin"
}
```

---

## ML Service API (FastAPI)

### 1. POST `/predict/ensemble`
Evaluate a feature vector against the multi-model ensemble.
* **Payload:**
```json
{
  "feature_vector": [1500.0, 2500.0, 15.0, 266.6, 2.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 350.0, 266.6, 0.0066, 30.0, 0.0, 0.0, 0.6, 0.0, 1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
  "source_ip": "192.168.1.105",
  "request_id": "req-83b6"
}
```
* **Response (200 OK):**
```json
{
  "isolation_forest": {
    "anomaly_score": -0.12,
    "is_anomaly": false
  },
  "xgboost": {
    "predicted_label": "BENIGN",
    "confidence": 0.99
  },
  "lstm": null,
  "final_severity": "LOW",
  "is_threat": false,
  "confidence": 0.99,
  "request_id": "req-83b6"
}
```

---

## Live WebSockets

* **URL:** `ws://localhost:8000/ws/alerts/`
* **Description:** Emits a JSON alert payload instantly whenever the AlertEngine registers a threat with severity above LOW.
