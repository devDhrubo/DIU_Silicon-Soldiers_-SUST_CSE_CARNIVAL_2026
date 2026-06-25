# QueueStorm Ticket Classifier

**bKash · SUST CSE Carnival 2026 · Warmup Mock Preliminary**

A FastAPI service that classifies bKash customer support tickets into
`case_type`, `severity`, `department`, and generates an agent-readable summary.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Liveness check (< 10 s) |
| `POST` | `/sort-ticket` | Classify one ticket (< 30 s) |
| `GET`  | `/docs` | Auto-generated Swagger UI |

---

## Local Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd queuestorm-api

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env template (no real values needed for rule-based version)
cp .env.example .env

# 5. Start the dev server
uvicorn main:app --reload
# → http://localhost:8000
```

---

## Test All 5 Sample Cases Locally

```bash
BASE=http://localhost:8000

# Health check
curl -s $BASE/health

# Case 1 — wrong transfer (expected: wrong_transfer, high)
curl -s -X POST $BASE/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-001","message":"I sent 3000 to wrong number"}'

# Case 2 — payment failed (expected: payment_failed, high)
curl -s -X POST $BASE/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-002","message":"Payment failed but balance deducted"}'

# Case 3 — phishing (expected: phishing_or_social_engineering, critical, human_review=true)
curl -s -X POST $BASE/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-003","message":"Someone called asking my OTP, is that bKash?"}'

# Case 4 — refund (expected: refund_request, low)
curl -s -X POST $BASE/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-004","message":"Please refund my last transaction, I changed my mind"}'

# Case 5 — other (expected: other, low)
curl -s -X POST $BASE/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-005","message":"App crashed when I opened it"}'
```

---

## Error Responses

| Status | Trigger | Example |
|--------|---------|---------|
| `422 Unprocessable Entity` | Missing `ticket_id` or `message` | `{"detail": [{"loc": ["body","message"],"msg":"field required",...}]}` |

---

## Verify Response Time SLA

```bash
# /health must respond < 10 s
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://<your-url>/health

# /sort-ticket must respond < 30 s
curl -o /dev/null -s -w "Time: %{time_total}s\n" -X POST https://<your-url>/sort-ticket \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"T-001","message":"I sent 3000 to wrong number"}'
```

---

## Deploy to Render

1. Push this repo to GitHub (public)
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Set these values:

   | Field | Value |
   |-------|-------|
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | **Instance Type** | Free |

5. Click **Deploy**. Wait for the build to finish.
6. Hit `/health` in your browser — keep refreshing until it responds (Render free tier cold-starts in 30–60 s).
7. Copy the HTTPS URL → submit via Google Form.

> **Note:** No environment variables are required for the rule-based version.
> If you add LLM support later, add your API key in Render → Environment tab.

---

## Stack

- Python 3.11
- FastAPI 0.111 + Uvicorn 0.29
- Pydantic v2
- No GPU, no external API calls, no secrets required
