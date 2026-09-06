"""Interactive terminal chat with the grocery agent, for local testing."""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

from app.grocery_agent import GroceryAgent  # noqa: E402  (must load .env first)


def main() -> None:
    grocery_agent = GroceryAgent()
    conversation_history: list = []

    print("Groceries bot CLI. Type 'exit' to quit.")
    while True:
        user_message = input("you> ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break
        if not user_message:
            continue
        reply_text, conversation_history = grocery_agent.respond(user_message, conversation_history)
        print(f"agent> {reply_text}")


if __name__ == "__main__":
    main()
