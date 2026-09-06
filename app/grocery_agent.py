"""Claude-backed conversational agent for managing the grocery list."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import anthropic

from app.agent_tools import TOOL_SCHEMAS, dispatch_tool_call
from app.grocery_database import GroceryDatabase

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
DATA_FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "groceries.md"

SYSTEM_PROMPT = """You are the grocery assistant for a household shared between two \
spouses. They will message you (eventually from a shared WhatsApp group) to add, \
remove, or check items on their grocery list, and to ask you to execute the order.

Use the provided tools to read and modify the grocery list — never guess at its \
contents, always call list_items if you need to check something first. When a \
message mentions multiple items, call the appropriate tool once per item. Keep \
your replies short and conversational, confirming what changed.

If asked to execute the order, call execute_order and relay its response \
honestly — do not claim to have placed an order if the tool says the feature \
is not implemented yet."""


class GroceryAgent:
    """Wraps an Anthropic client + tool-use loop around a GroceryDatabase."""

    def __init__(self, grocery_database: GroceryDatabase | None = None, model: str = DEFAULT_MODEL):
        self.anthropic_client = anthropic.Anthropic()
        self.grocery_database = grocery_database or GroceryDatabase(DATA_FILE_PATH)
        self.model = model

    def respond(self, user_message: str, conversation_history: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
        """Send a user message through the tool-use loop.

        Returns the assistant's final text reply and the updated conversation
        history (including this turn) to pass back in on the next call.
        """
        messages = conversation_history + [{"role": "user", "content": user_message}]

        while True:
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                final_text = "".join(block.text for block in response.content if block.type == "text")
                return final_text, messages

            tool_result_blocks = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                result_text = dispatch_tool_call(self.grocery_database, block.name, block.input)
                tool_result_blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    }
                )
            messages.append({"role": "user", "content": tool_result_blocks})
