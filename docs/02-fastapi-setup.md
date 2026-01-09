# FastAPI Application Setup

> **Configure FastAPI to work behind Nginx reverse proxy**

---

## Understanding `root_path`

When FastAPI runs behind a proxy (like Nginx) that adds a path prefix, use `root_path` so OpenAPI/Swagger UI generates correct URLs.

**Without it**: Docs generate `/openapi.json` (client can't find it)
**With it**: Docs generate `/python/openapi.json` (works correctly)

---

## Two Common Scenarios

### Scenario 1: No Path Prefix

**Public URL:** `https://api.example.com/`

**Nginx:**
```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
}
```

**FastAPI:**
```python
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

- ✅ No root_path needed
- ✅ Routes work naturally
- ✅ Access: `https://api.example.com/health`

---

### Scenario 2: With Path Prefix `/python`

**Public URL:** `https://api.example.com/python`

**Nginx:**
```nginx
location /python {
    proxy_pass http://127.0.0.1:8000;
}
```

**FastAPI:**
```python
app = FastAPI(root_path="/python")

@app.get("/health")
def health():
    return {"status": "ok"}
```

- ✅ `root_path="/python"` for docs
- ✅ Routes defined without prefix
- ✅ FastAPI receives `/python/health`
- ✅ Access: `https://api.example.com/python/health`

---

## Minimal Working Example

**File: `main.py`**

```python
from fastapi import FastAPI
from pydantic import BaseModel

# Use root_path when behind proxy with path prefix
app = FastAPI(
    root_path="/python",  # For Swagger UI to work behind /python proxy
    title="My API",
    version="1.0.0"
)

class TaskRequest(BaseModel):
    email: str
    message: str

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/users")
def get_users():
    return {"users": ["Alice", "Bob"]}

@app.post("/send-email")
def send_email(task: TaskRequest):
    # Queue with Celery (see tasks.py)
    from tasks import send_email_task
    result = send_email_task.delay(task.email, task.message)
    return {"task_id": str(result.id)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
```

**Access routes:**
- `https://api.example.com/python/` → root
- `https://api.example.com/python/health` → health check
- `https://api.example.com/python/users` → users list
- `https://api.example.com/python/docs` → Swagger UI

---

## Nginx Configuration

Your Nginx must match the `root_path`:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location /python {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Key point:** Nginx location `/python` matches FastAPI `root_path="/python"`

---

## Project Structure

```
your-project/
├── main.py              # FastAPI app
├── tasks.py             # Celery tasks
├── requirements.txt     # Dependencies
└── .env                 # Secrets (don't commit!)
```

**requirements.txt:**
```
fastapi
uvicorn[standard]
celery
redis
pydantic
```

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# In another terminal - run Celery worker
celery -A tasks worker --loglevel=info
```

Access: `http://localhost:8000/python/docs`

---

## What's Next?

1. [Create systemd Services](03-systemd-services.md) - Run as background services
2. [Configure Nginx](04-nginx-config.md) - Setup reverse proxy

---

## Quick Reference

| Item | Value |
|------|-------|
| Port | `8000` (localhost) |
| root_path | `/python` |
| Routes | `/health`, `/users` (no prefix in code) |
| Public URLs | `https://domain.com/python/health` |
| Docs | `https://domain.com/python/docs` |
