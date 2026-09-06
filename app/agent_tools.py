"""Tool schemas and dispatch for the grocery agent's Claude tool use."""

from __future__ import annotations

from typing import Any

from app.grocery_database import GroceryDatabase

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "add_item",
        "description": (
            "Add a grocery item to the list, or increase its quantity if it is "
            "already on the list."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the grocery item."},
                "quantity": {
                    "type": "integer",
                    "description": "How many units to add. Defaults to 1.",
                },
                "note": {
                    "type": "string",
                    "description": "Optional note, e.g. brand or preference.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "remove_item",
        "description": (
            "Remove a grocery item from the list, or reduce its quantity. "
            "Omit quantity to remove the item entirely."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the grocery item."},
                "quantity": {
                    "type": "integer",
                    "description": "How many units to remove. Omit to remove the item entirely.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "set_quantity",
        "description": "Set the exact quantity of a grocery item, adding it if not present.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the grocery item."},
                "quantity": {"type": "integer", "description": "Exact quantity to set."},
                "note": {"type": "string", "description": "Optional note to set or update."},
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "name": "list_items",
        "description": "List every item currently on the grocery list with quantities and notes.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "clear_list",
        "description": "Remove every item from the grocery list.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "execute_order",
        "description": (
            "Execute the grocery order. Currently a stub: Rami Levy integration "
            "is not implemented yet."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


def _format_item_list(items) -> str:
    if not items:
        return "The grocery list is empty."
    lines = [f"- {item.name}: {item.quantity}" + (f" ({item.note})" if item.note else "") for item in items]
    return "\n".join(lines)


def dispatch_tool_call(grocery_database: GroceryDatabase, tool_name: str, tool_input: dict[str, Any]) -> str:
    if tool_name == "add_item":
        item = grocery_database.add_item(
            name=tool_input["name"],
            quantity=tool_input.get("quantity", 1),
            note=tool_input.get("note"),
        )
        return f"'{item.name}' is now at quantity {item.quantity}."

    if tool_name == "remove_item":
        return grocery_database.remove_item(
            name=tool_input["name"],
            quantity=tool_input.get("quantity"),
        )

    if tool_name == "set_quantity":
        item = grocery_database.set_quantity(
            name=tool_input["name"],
            quantity=tool_input["quantity"],
            note=tool_input.get("note"),
        )
        return f"'{item.name}' set to quantity {item.quantity}."

    if tool_name == "list_items":
        return _format_item_list(grocery_database.list_items())

    if tool_name == "clear_list":
        grocery_database.clear()
        return "The grocery list has been cleared."

    if tool_name == "execute_order":
        return (
            "Order execution is not implemented yet. Phase 2 will create a Rami "
            "Levy cart and send back a checkout link."
        )

    raise ValueError(f"Unknown tool: {tool_name}")
