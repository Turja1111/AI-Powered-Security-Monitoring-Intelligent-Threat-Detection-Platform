"""Celery application for AI Security Monitoring Platform."""
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("security_monitoring")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ── Beat schedule ─────────────────────────────────────────────────────────────
app.conf.beat_schedule = {
    "process-feature-window": {
        "task": "apps.pipeline.tasks.process_feature_window",
        "schedule": 300.0,
    },
    "run-batch-inference": {
        "task": "apps.pipeline.tasks.run_batch_inference",
        "schedule": 300.0,
    },
    "trigger-alert-engine": {
        "task": "apps.pipeline.tasks.trigger_alert_engine",
        "schedule": 300.0,
    },
    "retrain-models": {
        "task": "apps.pipeline.tasks.retrain_models",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),
    },
    "cleanup-old-logs": {
        "task": "apps.pipeline.tasks.cleanup_old_logs",
        "schedule": crontab(hour=1, minute=0),
    },
    "generate-daily-report": {
        "task": "apps.pipeline.tasks.generate_daily_report",
        "schedule": crontab(hour=8, minute=0),
    },
}
