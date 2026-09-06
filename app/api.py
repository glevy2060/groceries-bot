"""REST API exposing the grocery agent. Later phases (WhatsApp) call /chat."""

from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

from app.grocery_agent import GroceryAgent  # noqa: E402  (must load .env first)

app = FastAPI(title="Groceries Bot")
grocery_agent = GroceryAgent()

conversation_histories: dict[str, list[dict[str, Any]]] = {}


class ChatRequest(BaseModel):
    message: str
    session_identifier: str = "default"


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(chat_request: ChatRequest) -> ChatResponse:
    history = conversation_histories.get(chat_request.session_identifier, [])
    reply_text, updated_history = grocery_agent.respond(chat_request.message, history)
    conversation_histories[chat_request.session_identifier] = updated_history
    return ChatResponse(reply=reply_text)


@app.get("/items")
def get_items() -> list[dict[str, Any]]:
    return [
        {"name": item.name, "quantity": item.quantity, "note": item.note}
        for item in grocery_agent.grocery_database.list_items()
    ]
