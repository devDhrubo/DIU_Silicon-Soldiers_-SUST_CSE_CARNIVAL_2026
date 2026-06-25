import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import TicketRequest, TicketResponse
from classifier import classify

load_dotenv()

app = FastAPI(title="QueueStorm API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "QueueStorm API is running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "queuestorm-classifier"}

@app.post("/sort-ticket", response_model=TicketResponse)
def sort_ticket(body: TicketRequest):
    result = classify(body.message)
    return TicketResponse(ticket_id=body.ticket_id, **result)
