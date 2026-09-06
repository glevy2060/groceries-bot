"""Tool schemas and dispatch for the grocery agent's Claude tool use."""

from __future__ import annotations

import json
from typing import Any

from app.grocery_database import GroceryDatabase
from app.rami_levy_client import RamiLevyClient

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
            "Search for all items on the grocery list in Rami Levy's catalog and prepare "
            "the order. If products are found, shows top matches for confirmation before "
            "creating the cart. Returns a checkout URL."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "finalize_order",
        "description": (
            "After confirming product selections, finalize the order and create the cart. "
            "Returns a checkout URL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_selections": {
                    "type": "string",
                    "description": (
                        "JSON string mapping item names to product IDs (from execute_order results). "
                        "E.g., '{\"חלב\": \"12345\", \"לחם\": \"67890\"}'"
                    ),
                },
            },
            "required": ["product_selections"],
        },
    },
]


def _format_item_list(items) -> str:
    if not items:
        return "The grocery list is empty."
    lines = [f"- {item.name}: {item.quantity}" + (f" ({item.note})" if item.note else "") for item in items]
    return "\n".join(lines)


def _execute_order_search(grocery_database: GroceryDatabase) -> str:
    """Search for items in Rami Levy catalog and return results for confirmation."""
    items = grocery_database.list_items()
    if not items:
        return "The grocery list is empty. Add items first, then execute the order."

    try:
        rami_levy = RamiLevyClient()
    except ValueError as e:
        return f"❌ Rami Levy auth failed: {e}. Set RAMI_LEVY_AUTH_TOKEN in .env"

    results: dict[str, Any] = {}
    search_failures: list[str] = []

    for item in items:
        try:
            products = rami_levy.search_catalog(item.name)
            if not products:
                search_failures.append(f"'{item.name}' (no results found)")
                continue
            top_matches = products[:3]
            results[item.name] = {
                "quantity": item.quantity,
                "matches": [
                    {
                        "id": p.get("id"),
                        "name": p.get("name", "Unknown"),
                        "price": p.get("price", "N/A"),
                        "brand": p.get("manufacturer", ""),
                    }
                    for p in top_matches
                ],
            }
        except Exception as e:
            search_failures.append(f"'{item.name}' (search error: {e})")

    if not results and search_failures:
        return f"❌ No products found. Failures:\n" + "\n".join(f"  - {f}" for f in search_failures)

    message = "🛒 Found products for your order:\n\n"
    for item_name, item_data in results.items():
        message += f"**{item_name}** (qty: {item_data['quantity']}):\n"
        for idx, match in enumerate(item_data["matches"], 1):
            price_str = f"₪{match['price']}" if match["price"] != "N/A" else "price N/A"
            brand_str = f" - {match['brand']}" if match["brand"] else ""
            message += f"  {idx}. {match['name']}{brand_str} ({price_str}) [ID: {match['id']}]\n"
        message += "\n"

    if search_failures:
        message += "⚠️ Not found or failed:\n" + "\n".join(f"  - {f}" for f in search_failures)
        message += "\n\n"

    message += (
        "Please confirm by listing the product IDs you want "
        "(e.g., \"use 123 for חלב, 456 for לחם\"), or ask me to search differently."
    )
    return message


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
        return _execute_order_search(grocery_database)

    if tool_name == "finalize_order":
        selections_json = tool_input.get("product_selections", "{}")
        try:
            selections = json.loads(selections_json)
        except json.JSONDecodeError:
            return f"❌ Invalid selection format. Expected JSON, got: {selections_json}"

        items = grocery_database.list_items()
        cart_items = []

        for item in items:
            if item.name not in selections:
                return f"❌ Missing selection for '{item.name}'. Please provide all product IDs."
            product_id = selections[item.name]
            cart_items.append({"product_id": product_id, "quantity": item.quantity})

        try:
            rami_levy = RamiLevyClient()
            rami_levy.create_cart(cart_items)
            checkout_url = rami_levy.get_checkout_url()
            return f"✅ Cart created! Complete checkout here: {checkout_url}"
        except Exception as e:
            return f"❌ Failed to create cart: {e}"

    raise ValueError(f"Unknown tool: {tool_name}")
