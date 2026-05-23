import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app, app_state

@pytest.fixture(autouse=True)
def setup_mock_models():
    # Mock models and assign to app_state
    mock_if = MagicMock()
    mock_if.is_trained = True
    mock_if.predict.return_value = {"score": -0.15, "is_anomaly": False, "threshold": -0.5}
    app_state.isolation_forest = mock_if

    mock_xgb = MagicMock()
    mock_xgb.is_trained = True
    mock_xgb.predict.return_value = {
        "predicted_label": "BENIGN",
        "confidence": 0.98,
        "class_probabilities": {"BENIGN": 0.98, "DDoS": 0.01, "PortScan": 0.01}
    }
    mock_xgb.explain.return_value = {
        "shap_values": {"feature_1": 0.05, "feature_2": -0.02},
        "top_features": [{"feature": "feature_1", "importance": 0.05}]
    }
    app_state.xgboost_classifier = mock_xgb

    mock_lstm = MagicMock()
    mock_lstm.is_trained = True
    mock_lstm.predict.return_value = {"reconstruction_error": 0.02, "is_anomaly": False, "threshold": 0.10}
    app_state.lstm_detector = mock_lstm

    mock_ensemble = MagicMock()
    mock_ensemble.predict_all.return_value = {
        "isolation_forest": {"score": -0.15, "is_anomaly": False},
        "xgboost": {"predicted_label": "BENIGN", "confidence": 0.98},
        "lstm": {"reconstruction_error": 0.02, "is_anomaly": False},
        "final_severity": "LOW",
        "is_threat": False,
        "confidence": 0.98
    }
    app_state.ensemble_predictor = mock_ensemble
    app_state.model_load_errors = {}

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def headers():
    return {"X-API-Key": "ml-service-internal-key-change-me"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models"]["isolation_forest"]["loaded"] is True
    assert data["models"]["xgboost"]["loaded"] is True
    assert data["models"]["lstm"]["loaded"] is True

def test_unauthorized_access(client):
    response = client.post("/predict/isolation-forest", json={"feature_vector": [1.0] * 26})
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid or missing API key"

def test_predict_isolation_forest(client, headers):
    response = client.post(
        "/predict/isolation-forest",
        json={"feature_vector": [0.1] * 26, "request_id": "req-123"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "anomaly_score" in data
    assert data["is_anomaly"] is False
    assert data["request_id"] == "req-123"

def test_predict_xgboost(client, headers):
    response = client.post(
        "/predict/xgboost",
        json={"feature_vector": [0.2] * 26, "request_id": "req-456"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_label"] == "BENIGN"
    assert data["confidence"] == 0.98
    assert "shap_values" in data
    assert data["request_id"] == "req-456"

def test_predict_lstm(client, headers):
    response = client.post(
        "/predict/lstm",
        json={"sequence": [[0.1] * 26] * 20, "request_id": "req-789"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "reconstruction_error" in data
    assert data["is_anomaly"] is False
    assert data["request_id"] == "req-789"

def test_predict_ensemble(client, headers):
    response = client.post(
        "/predict/ensemble",
        json={"feature_vector": [0.1] * 26, "request_id": "req-999"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["final_severity"] == "LOW"
    assert data["is_threat"] is False
    assert data["confidence"] == 0.98
    assert data["request_id"] == "req-999"

def test_get_active_models(client, headers):
    response = client.get("/models/active", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert any(m["name"] == "xgboost_classifier" for m in data)

def test_reload_models(client, headers):
    response = client.post("/models/reload", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reloaded"
    assert "xgboost_classifier" in data["models_reloaded"]
