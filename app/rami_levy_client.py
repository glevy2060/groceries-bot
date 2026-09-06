"""Client for Rami Levy e-commerce API (internal/reverse-engineered endpoints)."""

from __future__ import annotations

import os
from typing import Any

import requests

RAMI_LEVY_API_BASE = "https://www.rami-levy.co.il"
DEFAULT_STORE_ID = 331
CHECKOUT_URL = f"{RAMI_LEVY_API_BASE}/he/dashboard/checkout"


class RamiLevyClient:
    """Interact with Rami Levy's internal web APIs."""

    def __init__(self, auth_token: str | None = None):
        self.auth_token = auth_token or os.environ.get("RAMI_LEVY_AUTH_TOKEN")
        if not self.auth_token:
            raise ValueError("RAMI_LEVY_AUTH_TOKEN not set in environment")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json",
            }
        )

    def search_catalog(self, query: str, store_id: int = DEFAULT_STORE_ID) -> list[dict[str, Any]]:
        """Search for products in the catalog.

        Args:
            query: Product name (e.g., "חלב" for milk)
            store_id: Rami Levy store ID

        Returns:
            List of matching products (top results first)
        """
        response = self.session.post(
            f"{RAMI_LEVY_API_BASE}/api/catalog",
            json={"aggs": 1, "q": query, "store": store_id},
        )
        response.raise_for_status()
        data = response.json()
        products = data.get("results", [])
        return products

    def create_cart(self, items: list[dict[str, int]]) -> dict[str, Any]:
        """Create or update a cart with items.

        Args:
            items: List of dicts with 'product_id' and 'quantity'

        Returns:
            Cart response (includes cart_id, session_id, etc.)
        """
        response = self.session.post(
            f"{RAMI_LEVY_API_BASE}/api/v2/cart",
            json={"items": items},
        )
        response.raise_for_status()
        return response.json()

    def get_checkout_url(self) -> str:
        """Return the checkout page URL."""
        return CHECKOUT_URL
