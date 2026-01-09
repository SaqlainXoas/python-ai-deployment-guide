"""
Celery tasks for background processing
"""

from celery import Celery
import time
import os

# Configure Celery
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name='tasks.send_email_task')
def send_email_task(email: str, message: str):
    """
    Simulate sending an email
    In production, replace with actual email service (SendGrid, SES, etc.)
    """
    print(f"Starting email task for: {email}")

    # Simulate email processing time
    time.sleep(5)

    print(f"Email sent to {email}: {message}")

    return {
        "status": "sent",
        "email": email,
        "message": message
    }


@celery_app.task(name='tasks.process_data_task')
def process_data_task(data: dict):
    """
    Simulate CPU-intensive data processing
    """
    print(f"Processing data: {data}")

    # Simulate processing time
    time.sleep(10)

    # Example processing
    result = {
        "processed": True,
        "input_keys": list(data.keys()),
        "timestamp": time.time()
    }

    print(f"Data processing complete: {result}")

    return result


@celery_app.task(name='tasks.periodic_cleanup_task')
def periodic_cleanup_task():
    """
    Example of a periodic task (requires celery beat)
    Run this every day at midnight to clean up old data
    """
    print("Running periodic cleanup task")

    # Your cleanup logic here
    time.sleep(2)

    return {
        "status": "completed",
        "cleaned_items": 42
    }


# Optional: Celery Beat schedule for periodic tasks
# To use this, run: celery -A tasks beat
celery_app.conf.beat_schedule = {
    'cleanup-every-day': {
        'task': 'tasks.periodic_cleanup_task',
        'schedule': 86400.0,  # 24 hours in seconds
    },
}
