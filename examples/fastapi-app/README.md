# Sample FastAPI + Celery Application

Complete working example of FastAPI with Celery background tasks and `root_path` configuration.

## Project Structure

```
fastapi-app/
├── main.py              # FastAPI application
├── tasks.py             # Celery tasks
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Features

- ✅ FastAPI web framework
- ✅ Celery for background tasks
- ✅ Redis as message broker
- ✅ `root_path="/python"` for proxy deployment
- ✅ Health check endpoints
- ✅ Task status tracking

## API Endpoints

Routes are defined without `/python` prefix in code. FastAPI adds it automatically for docs.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health status |
| GET | `/users` | Sample users list |
| POST | `/send-email` | Queue email task |
| GET | `/task/{task_id}` | Check task status |
| POST | `/process-data` | Queue data processing |

**Public access** (through Nginx): `https://api.example.com/python/health`

## Local Development

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis

```bash
redis-cli ping
# Should return: PONG
```

### 3. Run FastAPI (Terminal 1)

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Run Celery Worker (Terminal 2)

```bash
celery -A tasks worker --loglevel=info
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/python/

# Swagger UI
open http://localhost:8000/python/docs

# Queue a task
curl -X POST http://localhost:8000/python/send-email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","message":"Hello!"}'

# Check task status
curl http://localhost:8000/python/task/TASK_ID
```

## Production Deployment

Follow the main guide in [docs/](../../docs/) for production setup with systemd and Nginx.

## Notes

- Uses `root_path="/python"` for OpenAPI/Swagger UI compatibility
- FastAPI runs on port 8000 (localhost only)
- Celery tasks are processed asynchronously
- Redis required for message broker and result backend
