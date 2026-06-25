"""
main.py
-------
QueueStorm Warmup API — FastAPI entry point.

Endpoints:
  GET  /health       → service liveness check
  POST /sort-ticket  → classify one CRM ticket
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import TicketRequest, TicketResponse
from classifier import classify

load_dotenv()

app = FastAPI(
    title="QueueStorm Ticket Classifier",
    description=(
        "bKash · SUST CSE Carnival 2026 · Warmup Mock Preliminary. "
        "Classifies customer support tickets into case type, severity, and department."
    ),
    version="1.0.0",
)

# ── CORS (graders may test from browser tools) ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health():
    """
    Simple liveness check. Must respond within 10 seconds.
    """
    return {"status": "ok", "service": "queuestorm-classifier"}


# ── Sort Ticket ───────────────────────────────────────────────────────────────

@app.post("/sort-ticket", response_model=TicketResponse, tags=["Classification"])
def sort_ticket(body: TicketRequest):
    """
    Accept one CRM ticket and return structured classification.

    - Missing `ticket_id` or `message` → **422 Unprocessable Entity**
    - Must respond within 30 seconds (typically < 50 ms for rule-based).
    """
    result = classify(body.message)
    return TicketResponse(ticket_id=body.ticket_id, **result)
