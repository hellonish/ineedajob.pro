"""
Celery Configuration
"""

import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "wand",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["api.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minute timeout per task
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_concurrency=3,  # Max 3 concurrent workers
)
