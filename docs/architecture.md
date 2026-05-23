# System Architecture Description

This document details the components and data flows of the AI-Powered Security Monitoring & Intelligent Threat Detection Platform.

## System Topology Diagram

```
+---------------------------------------------------------------------------------+
|                                 LOG INGESTION                                   |
|                                                                                 |
|   +-----------------------+              +---------------------------------+    |
|   |  MQTT Edge Client(s)  |              |    REST API (Django Daphne)     |    |
|   |  (Local ONNX Scoring) |              |    Ingests Live Logs & CSVs     |    |
|   +-----------+-----------+              +----------------+----------------+    |
+---------------|-------------------------------------------|---------------------+
                | (Publish Alert)                           | (Ingest Event)
                v                                           v
+---------------------------------------------------------------------------------+
|                                MESSAGING STEAM                                  |
|                                                                                 |
|                       +---------------------------------+                       |
|                       |      Apache Kafka Broker        |                       |
|                       |      Topic: "raw-logs"          |                       |
|                       +----------------+----------------+                       |
+----------------------------------------|----------------------------------------+
                                         | (Consume Stream)
                                         v
+---------------------------------------------------------------------------------+
|                               PIPELINE ENGINE                                   |
|                                                                                 |
|                       +---------------------------------+                       |
|                       |   Kafka Consumer Worker         |                       |
|                       |   computes sliding 5m features  |                       |
|                       +----------------+----------------+                       |
+----------------------------------------|----------------------------------------+
                                         | (Inference Request)
                                         v
+---------------------------------------------------------------------------------+
|                             ML ENSEMBLE ENGINE                                  |
|                                                                                 |
|  +---------------------------------------------------------------------------+  |
|  |                           FastAPI Microservice                            |  |
|  |                                                                           |  |
|  |   +------------------------+  +--------------------+  +---------------+   |  |
|  |   | Isolation Forest (Un)  |  | XGBoost (Multi)    |  | PyTorch LSTM  |   |  |
|  |   +-----------+------------+  +---------+----------+  +-------+-------+   |  |
|  |               |                         |                     |           |  |
|  |               +-------------------------+---------------------+           |  |
|  |                                         v                                 |  |
|  |                                Ensemble Predictor                         |  |
|  |                                         |                                 |  |
|  +-----------------------------------------|---------------------------------+  |
+--------------------------------------------|------------------------------------+
                                             | (Alert persist & WS dispatch)
                                             v
+---------------------------------------------------------------------------------+
|                                ALERTS & DISPATCH                                |
|                                                                                 |
|   +-----------------------+              +---------------------------------+    |
|   |   TimescaleDB Store   |              |   Django Channels WebSocket     |    |
|   |   (Log & Alert DB)    |              |   Pushes to React Dashboard     |    |
|   +-----------------------+              +---------------------------------+    |
+---------------------------------------------------------------------------------+
```

## Data Flow Details

1. **Ingestion Layer:** Live logs are received via `/api/v1/logs/event/` on the Daphne server. Daphne saves logs to TimescaleDB and pushes them asynchronously onto Kafka's `raw-logs` topic.
2. **Streaming Pipeline:** The Pipeline consumer reads log events, aggregates logs for that specific Source IP over the last 5 minutes, builds a 26-feature vector, and forwards it to the ML Service.
3. **ML Service:** Preprocesses features with a standardized scaler, evaluates anomaly scores with Isolation Forest, maps threats to specific classes using XGBoost, and processes sequences using LSTM.
4. **Alerts & Visualization:** The Alert Engine runs deduplication (collapsing identical IP alarms inside a TTL window), logs verified threats to the DB, and dispatches them via WebSockets to the React app.
