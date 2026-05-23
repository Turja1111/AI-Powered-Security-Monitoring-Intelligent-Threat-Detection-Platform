"""
ML Service — Main FastAPI Application
AI-Powered Security Monitoring Platform
"""
from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

import httpx
import redis.asyncio as aioredis
from decouple import config
from fastapi import Depends, FastAPI, HTTPException, Request, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field

from models.isolation_forest import IsolationForestModel
from models.lstm_detector import LSTMDetector
from models.xgboost_classifier import XGBoostClassifier
from serving.predictor import EnsemblePredictor
from serving.preprocessor import Preprocessor

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("ml_service")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_ARTIFACTS_DIR = config("MODEL_ARTIFACTS_DIR", default="model-artifacts")
MLFLOW_TRACKING_URI = config("MLFLOW_TRACKING_URI", default="http://mlflow:5000")
ML_SERVICE_API_KEY = config("ML_SERVICE_API_KEY", default="ml-service-internal-key-change-me")
REDIS_URL = config("REDIS_URL", default="redis://cache:6379/0")
CORS_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="http://localhost:3000").split(",")

# ---------------------------------------------------------------------------
# API key auth
# ---------------------------------------------------------------------------
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    if api_key != ML_SERVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return api_key


# ---------------------------------------------------------------------------
# Global state — models loaded at startup
# ---------------------------------------------------------------------------
class AppState:
    isolation_forest: IsolationForestModel | None = None
    xgboost_classifier: XGBoostClassifier | None = None
    lstm_detector: LSTMDetector | None = None
    preprocessor: Preprocessor | None = None
    ensemble_predictor: EnsemblePredictor | None = None
    redis_client: aioredis.Redis | None = None
    model_load_time: float = 0.0
    model_load_errors: dict[str, str] = {}


app_state = AppState()


def _load_models() -> None:
    """Load all models from disk. Called at startup and on reload."""
    errors: dict[str, str] = {}

    # --- Preprocessor (scaler) ---
    try:
        app_state.preprocessor = Preprocessor()
        scaler_path = os.path.join(MODEL_ARTIFACTS_DIR, "scaler.joblib")
        if os.path.exists(scaler_path):
            app_state.preprocessor.load_scaler(scaler_path)
            logger.info("Scaler loaded from %s", scaler_path)
        else:
            logger.warning("Scaler not found at %s — using unscaled features", scaler_path)
    except Exception as exc:
        logger.error("Failed to load scaler: %s", exc)
        errors["preprocessor"] = str(exc)
        app_state.preprocessor = Preprocessor()  # fallback

    # --- Isolation Forest ---
    try:
        app_state.isolation_forest = IsolationForestModel()
        if_path = os.path.join(MODEL_ARTIFACTS_DIR, "isolation_forest.joblib")
        if os.path.exists(if_path):
            app_state.isolation_forest.load(if_path)
            logger.info("IsolationForest loaded from %s", if_path)
        else:
            logger.warning("IsolationForest model not found — using untrained model")
    except Exception as exc:
        logger.error("Failed to load IsolationForest: %s", exc)
        errors["isolation_forest"] = str(exc)

    # --- XGBoost ---
    try:
        app_state.xgboost_classifier = XGBoostClassifier()
        xgb_path = os.path.join(MODEL_ARTIFACTS_DIR, "xgboost_classifier.joblib")
        if os.path.exists(xgb_path):
            app_state.xgboost_classifier.load(xgb_path)
            logger.info("XGBoostClassifier loaded from %s", xgb_path)
        else:
            logger.warning("XGBoost model not found — using untrained model")
    except Exception as exc:
        logger.error("Failed to load XGBoost: %s", exc)
        errors["xgboost"] = str(exc)

    # --- LSTM ---
    try:
        app_state.lstm_detector = LSTMDetector()
        lstm_path = os.path.join(MODEL_ARTIFACTS_DIR, "lstm_detector.pt")
        if os.path.exists(lstm_path):
            app_state.lstm_detector.load(lstm_path)
            logger.info("LSTMDetector loaded from %s", lstm_path)
        else:
            logger.warning("LSTM model not found — using untrained model")
    except Exception as exc:
        logger.error("Failed to load LSTM: %s", exc)
        errors["lstm"] = str(exc)

    # --- Ensemble predictor ---
    app_state.ensemble_predictor = EnsemblePredictor(
        isolation_forest=app_state.isolation_forest,
        xgboost_classifier=app_state.xgboost_classifier,
        lstm_detector=app_state.lstm_detector,
    )

    app_state.model_load_time = time.time()
    app_state.model_load_errors = errors
    logger.info("Model loading complete. Errors: %s", errors or "none")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: load models and connect to Redis on startup."""
    logger.info("=== ML Service starting up ===")

    # Load models
    _load_models()

    # Connect to Redis (optional — non-fatal if unavailable)
    try:
        app_state.redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
        await app_state.redis_client.ping()
        logger.info("Redis connection established: %s", REDIS_URL)
    except Exception as exc:
        logger.warning("Redis unavailable (%s) — caching disabled", exc)
        app_state.redis_client = None

    logger.info("=== ML Service ready ===")
    yield

    # Shutdown
    logger.info("=== ML Service shutting down ===")
    if app_state.redis_client:
        await app_state.redis_client.aclose()


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Security Monitoring — ML Service",
    description="Model inference API for anomaly detection and threat classification",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d  (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Response-Time-Ms"] = f"{duration_ms:.1f}"
    return response


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
class FeatureVectorRequest(BaseModel):
    feature_vector: list[float] = Field(
        ..., min_length=1, description="Normalized feature vector"
    )
    source_ip: str | None = Field(None, description="Optional source IP for logging")
    request_id: str | None = Field(None, description="Optional correlation ID")


class SequenceRequest(BaseModel):
    sequence: list[list[float]] = Field(
        ..., min_length=1, description="Sequence of feature vectors (time-ordered)"
    )
    source_ip: str | None = None
    request_id: str | None = None


class IsolationForestResponse(BaseModel):
    anomaly_score: float
    is_anomaly: bool
    threshold: float
    request_id: str | None = None


class XGBoostResponse(BaseModel):
    predicted_label: str
    confidence: float
    class_probabilities: dict[str, float]
    shap_values: dict[str, float]
    top_features: list[dict[str, Any]]
    request_id: str | None = None


class LSTMResponse(BaseModel):
    reconstruction_error: float
    is_anomaly: bool
    threshold: float
    request_id: str | None = None


class EnsembleResponse(BaseModel):
    isolation_forest: dict[str, Any]
    xgboost: dict[str, Any]
    lstm: dict[str, Any] | None
    final_severity: str
    is_threat: bool
    confidence: float
    request_id: str | None = None


class ModelInfo(BaseModel):
    name: str
    version: str
    loaded: bool
    load_time_epoch: float
    metrics: dict[str, Any]


class ReloadResponse(BaseModel):
    status: str
    models_reloaded: list[str]
    errors: dict[str, str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _require_if_model() -> IsolationForestModel:
    if app_state.isolation_forest is None:
        raise HTTPException(status_code=503, detail="IsolationForest model not loaded")
    return app_state.isolation_forest


def _require_xgb_model() -> XGBoostClassifier:
    if app_state.xgboost_classifier is None:
        raise HTTPException(status_code=503, detail="XGBoost model not loaded")
    return app_state.xgboost_classifier


def _require_lstm_model() -> LSTMDetector:
    if app_state.lstm_detector is None:
        raise HTTPException(status_code=503, detail="LSTM model not loaded")
    return app_state.lstm_detector


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["ops"])
async def health_check() -> dict[str, Any]:
    """Health check with model loading status."""
    status_info: dict[str, Any] = {
        "status": "healthy",
        "timestamp": time.time(),
        "models": {
            "isolation_forest": {
                "loaded": app_state.isolation_forest is not None and app_state.isolation_forest.is_trained,
            },
            "xgboost": {
                "loaded": app_state.xgboost_classifier is not None and app_state.xgboost_classifier.is_trained,
            },
            "lstm": {
                "loaded": app_state.lstm_detector is not None and app_state.lstm_detector.is_trained,
            },
        },
        "model_load_time_epoch": app_state.model_load_time,
        "load_errors": app_state.model_load_errors,
        "redis_connected": app_state.redis_client is not None,
    }

    # If no models loaded, service is degraded
    all_loaded = all(m["loaded"] for m in status_info["models"].values())
    if not all_loaded and app_state.model_load_errors:
        status_info["status"] = "degraded"

    return status_info


@app.post(
    "/predict/isolation-forest",
    response_model=IsolationForestResponse,
    tags=["inference"],
    dependencies=[Depends(verify_api_key)],
)
async def predict_isolation_forest(body: FeatureVectorRequest) -> IsolationForestResponse:
    """
    Anomaly detection using Isolation Forest.
    Returns anomaly score and binary is_anomaly flag.
    """
    model = _require_if_model()
    try:
        result = model.predict(body.feature_vector)
        return IsolationForestResponse(
            anomaly_score=result["score"],
            is_anomaly=result["is_anomaly"],
            threshold=result["threshold"],
            request_id=body.request_id,
        )
    except Exception as exc:
        logger.exception("IsolationForest prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc


@app.post(
    "/predict/xgboost",
    response_model=XGBoostResponse,
    tags=["inference"],
    dependencies=[Depends(verify_api_key)],
)
async def predict_xgboost(body: FeatureVectorRequest) -> XGBoostResponse:
    """
    Multi-class attack classification using XGBoost.
    Returns predicted attack label, confidence, and SHAP explanations.
    """
    model = _require_xgb_model()
    try:
        pred = model.predict(body.feature_vector)
        explanation = model.explain(body.feature_vector)
        return XGBoostResponse(
            predicted_label=pred["predicted_label"],
            confidence=pred["confidence"],
            class_probabilities=pred["class_probabilities"],
            shap_values=explanation["shap_values"],
            top_features=explanation["top_features"],
            request_id=body.request_id,
        )
    except Exception as exc:
        logger.exception("XGBoost prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc


@app.post(
    "/predict/lstm",
    response_model=LSTMResponse,
    tags=["inference"],
    dependencies=[Depends(verify_api_key)],
)
async def predict_lstm(body: SequenceRequest) -> LSTMResponse:
    """
    Sequence anomaly detection using LSTM autoencoder.
    Returns reconstruction error and is_anomaly flag.
    """
    model = _require_lstm_model()
    try:
        result = model.predict(body.sequence)
        return LSTMResponse(
            reconstruction_error=result["reconstruction_error"],
            is_anomaly=result["is_anomaly"],
            threshold=result["threshold"],
            request_id=body.request_id,
        )
    except Exception as exc:
        logger.exception("LSTM prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc


@app.post(
    "/predict/ensemble",
    response_model=EnsembleResponse,
    tags=["inference"],
    dependencies=[Depends(verify_api_key)],
)
async def predict_ensemble(body: FeatureVectorRequest) -> EnsembleResponse:
    """
    Ensemble prediction using all three models.
    Combines results to produce a final severity score.
    """
    if app_state.ensemble_predictor is None:
        raise HTTPException(status_code=503, detail="Ensemble predictor not initialized")

    try:
        result = app_state.ensemble_predictor.predict_all(body.feature_vector)

        # Cache result in Redis (fire-and-forget)
        if app_state.redis_client and body.request_id:
            try:
                import json
                await app_state.redis_client.setex(
                    f"predict:{body.request_id}",
                    300,  # 5 min TTL
                    json.dumps(result),
                )
            except Exception:
                pass  # Non-fatal

        return EnsembleResponse(
            isolation_forest=result["isolation_forest"],
            xgboost=result["xgboost"],
            lstm=result.get("lstm"),
            final_severity=result["final_severity"],
            is_threat=result["is_threat"],
            confidence=result["confidence"],
            request_id=body.request_id,
        )
    except Exception as exc:
        logger.exception("Ensemble prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc


@app.get(
    "/models/active",
    response_model=list[ModelInfo],
    tags=["models"],
    dependencies=[Depends(verify_api_key)],
)
async def get_active_models() -> list[ModelInfo]:
    """Returns list of currently loaded model versions with their metrics."""
    models: list[ModelInfo] = []

    if app_state.isolation_forest is not None:
        models.append(
            ModelInfo(
                name="isolation_forest",
                version=getattr(app_state.isolation_forest, "version", "1.0.0"),
                loaded=app_state.isolation_forest.is_trained,
                load_time_epoch=app_state.model_load_time,
                metrics=getattr(app_state.isolation_forest, "metadata", {}),
            )
        )

    if app_state.xgboost_classifier is not None:
        models.append(
            ModelInfo(
                name="xgboost_classifier",
                version=getattr(app_state.xgboost_classifier, "version", "1.0.0"),
                loaded=app_state.xgboost_classifier.is_trained,
                load_time_epoch=app_state.model_load_time,
                metrics=getattr(app_state.xgboost_classifier, "metadata", {}),
            )
        )

    if app_state.lstm_detector is not None:
        models.append(
            ModelInfo(
                name="lstm_detector",
                version=getattr(app_state.lstm_detector, "version", "1.0.0"),
                loaded=app_state.lstm_detector.is_trained,
                load_time_epoch=app_state.model_load_time,
                metrics=getattr(app_state.lstm_detector, "metadata", {}),
            )
        )

    return models


@app.post(
    "/models/reload",
    response_model=ReloadResponse,
    tags=["models"],
    dependencies=[Depends(verify_api_key)],
)
async def reload_models() -> ReloadResponse:
    """Hot-reload all models from disk / MLflow registry."""
    logger.info("Hot-reload requested")
    _load_models()

    reloaded = []
    if app_state.isolation_forest and app_state.isolation_forest.is_trained:
        reloaded.append("isolation_forest")
    if app_state.xgboost_classifier and app_state.xgboost_classifier.is_trained:
        reloaded.append("xgboost_classifier")
    if app_state.lstm_detector and app_state.lstm_detector.is_trained:
        reloaded.append("lstm_detector")

    return ReloadResponse(
        status="reloaded",
        models_reloaded=reloaded,
        errors=app_state.model_load_errors,
    )


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )
