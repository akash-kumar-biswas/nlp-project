from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import (
    init_db,
    create_ticket,
    get_all_tickets,
    update_ticket_status
)

from model_service import predict


app = FastAPI(
    title="E-Commerce NLP Support API"
)


class QueryRequest(BaseModel):
    query: str


class StatusRequest(BaseModel):
    status: str


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {
        "message": "E-Commerce NLP Support API is running"
    }


@app.post("/tickets")
def submit_ticket(data: QueryRequest):

    if not data.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    # Model prediction
    prediction = predict(data.query)

    # Store ticket
    ticket = create_ticket(
        query=data.query,
        subsystem=prediction["subsystem"],
        priority=prediction["priority"]
    )

    return ticket


@app.get("/tickets")
def tickets():
    return get_all_tickets()


@app.patch("/tickets/{ticket_id}/status")
def change_status(ticket_id: int, data: StatusRequest):
    if data.status not in {"Pending", "Resolved"}:
        raise HTTPException(
            status_code=400,
            detail="Status must be Pending or Resolved"
        )

    updated = update_ticket_status(
        ticket_id,
        data.status
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "message": "Status updated successfully",
        "ticket_id": ticket_id,
        "status": data.status,
    }