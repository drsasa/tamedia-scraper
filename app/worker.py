from __future__ import absolute_import

import os
import psycopg2

from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown


REDIS = os.getenv("REDIS")
BROKER = os.getenv("CELERY_BROKER_URL")
TIME_FRAME = os.getenv("TIME_FRAME")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

db_conn = None

app = Celery("celery_tasks", broker=BROKER, backend=BROKER)
app.conf.task_create_missing_queues = True
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1
app.conf.timezone = "Europe/Belgrade"
app.conf.enable_utc = True

max_timeout_in_seconds = 60 * 2  # 2min this is arbitrary
app.conf.broker_transport_options = {
    "priority_steps": list(range(10)),
    "queue_order_strategy": "priority",
    "visibility_timeout": max_timeout_in_seconds,
}

app.autodiscover_tasks(
    [
        "tasks",
    ],
    force=True,
)

app.conf.beat_schedule = {
    "fetch_source": {
        "task": "fetch_source",
        "schedule": float(TIME_FRAME),
        "args": None,
    }
}


@worker_process_init.connect
def init_worker(**kwargs):
    global db_conn

    db_conn = psycopg2.connect(
        database="postgres",
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user="postgres",
    )


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    global db_conn
    if db_conn:
        db_conn.close()
