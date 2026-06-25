# QueueStorm API

Submission for bKash SUST CSE Carnival 2026 Warmup Mock Preliminary.

A simple FastAPI service to classify customer support tickets into `case_type`, `severity`, and `department`.

## Endpoints

- `GET /health` : Liveness check
- `POST /sort-ticket` : Classify ticket
- `GET /docs` : Swagger UI

## How to run locally

```bash
git clone <your-repo>
cd queuestorm-api

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

uvicorn main:app --reload
```

## Testing

```bash
curl -s -X POST http://localhost:8000/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-001","message":"I sent 3000 to wrong number"}'
```

## Deployment on Render

1. Push to GitHub
2. Go to render.com -> New Web Service
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
