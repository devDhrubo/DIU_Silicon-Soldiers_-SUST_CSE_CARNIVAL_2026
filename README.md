# QueueStorm API

Submission for bKash SUST CSE Carnival 2026 Warmup Mock Preliminary.

A simple FastAPI service to classify customer support tickets into `case_type`, `severity`, and `department`.

## Endpoints

- `GET /health` : Liveness check
- `POST /sort-ticket` : Classify ticket
- `GET /docs` : Swagger UI

## How to run locally

```bash
git clone https://github.com/devDhrubo/DIU_Silicon-Soldiers_-SUST_CSE_CARNIVAL_2026.git
cd DIU_Silicon-Soldiers_-SUST_CSE_CARNIVAL_2026

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

## Deployment

Live URL: https://diu-silicon-soldiers-sust-cse-carnival.onrender.com/
