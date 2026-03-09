import os

from celery import Celery

celery = Celery(
    "redsnake",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://redsnake-redis:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://redsnake-redis:6379/0"),
)


@celery.task
def example_task(x, y):
    return x + y
