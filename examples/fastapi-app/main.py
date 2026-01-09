"""
FastAPI Application with Celery Integration
Minimal example with root_path for proxy deployment
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# root_path tells FastAPI it's behind a /python proxy
# This makes OpenAPI/Swagger UI docs work correctly
app = FastAPI(
    root_path="/python",
    title="Sample FastAPI App",
    description="FastAPI application with Celery background tasks",
    version="1.0.0"
)


# Models
class TaskRequest(BaseModel):
    email: str
    message: str


class TaskResponse(BaseModel):
    task_id: str
    status: str


# Routes - defined WITHOUT /python prefix
# FastAPI adds the prefix automatically for docs

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "FastAPI application is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "redis": check_redis_connection(),
        "celery": "connected"
    }


@app.get("/users")
def get_users():
    """Sample endpoint - get users"""
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
    }


@app.post("/send-email")
def send_email(task_request: TaskRequest):
    """Queue email sending task with Celery"""
    from tasks import send_email_task

    task = send_email_task.delay(
        email=task_request.email,
        message=task_request.message
    )

    return TaskResponse(
        task_id=str(task.id),
        status="queued"
    )


@app.get("/task/{task_id}")
def get_task_status(task_id: str):
    """Check status of a Celery task"""
    from celery.result import AsyncResult
    from tasks import celery_app

    task = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }


@app.post("/process-data")
def process_data(data: dict):
    """Example of CPU-intensive task sent to Celery"""
    from tasks import process_data_task

    task = process_data_task.delay(data)

    return {
        "task_id": str(task.id),
        "status": "processing",
        "message": "Data processing started in background"
    }


# Helper functions

def check_redis_connection():
    """Check if Redis is accessible"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return "connected"
    except Exception as e:
        return f"error: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
