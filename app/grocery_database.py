"""Naive markdown-file-backed grocery list database."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ITEMS_HEADER = "## Items"
LINE_PATTERN = re.compile(r"^- (?P<name>.+?) x(?P<quantity>\d+)(?: \((?P<note>.+)\))?$")


@dataclass
class GroceryItem:
    name: str
    quantity: int
    note: str | None = None

    def to_markdown_line(self) -> str:
        line = f"- {self.name} x{self.quantity}"
        if self.note:
            line += f" ({self.note})"
        return line


class GroceryDatabase:
    """Reads and writes grocery items to/from a markdown file.

    The file is the single source of truth; every method reads the current
    file state before mutating and writes it back immediately after.
    """

    def __init__(self, markdown_file_path: Path):
        self.markdown_file_path = markdown_file_path

    def list_items(self) -> list[GroceryItem]:
        text = self.markdown_file_path.read_text(encoding="utf-8")
        if ITEMS_HEADER not in text:
            return []
        items_section = text.split(ITEMS_HEADER, 1)[1]
        items: list[GroceryItem] = []
        for line in items_section.splitlines():
            line = line.strip()
            if not line:
                continue
            match = LINE_PATTERN.match(line)
            if match:
                items.append(
                    GroceryItem(
                        name=match.group("name"),
                        quantity=int(match.group("quantity")),
                        note=match.group("note"),
                    )
                )
        return items

    def _save_items(self, items: list[GroceryItem]) -> None:
        text = self.markdown_file_path.read_text(encoding="utf-8")
        preamble = text.split(ITEMS_HEADER, 1)[0] if ITEMS_HEADER in text else text
        preamble = preamble.rstrip("\n")
        lines = [item.to_markdown_line() for item in sorted(items, key=lambda item: item.name.lower())]
        items_section = "\n".join(lines)
        new_text = f"{preamble}\n\n{ITEMS_HEADER}\n"
        if items_section:
            new_text += f"{items_section}\n"
        self.markdown_file_path.write_text(new_text, encoding="utf-8")

    def _find_item_index(self, items: list[GroceryItem], name: str) -> int | None:
        normalized_name = name.strip().lower()
        for index, item in enumerate(items):
            if item.name.strip().lower() == normalized_name:
                return index
        return None

    def add_item(self, name: str, quantity: int = 1, note: str | None = None) -> GroceryItem:
        items = self.list_items()
        existing_index = self._find_item_index(items, name)
        if existing_index is not None:
            existing_item = items[existing_index]
            existing_item.quantity += quantity
            if note:
                existing_item.note = note
            updated_item = existing_item
        else:
            updated_item = GroceryItem(name=name, quantity=quantity, note=note)
            items.append(updated_item)
        self._save_items(items)
        return updated_item

    def remove_item(self, name: str, quantity: int | None = None) -> str:
        items = self.list_items()
        existing_index = self._find_item_index(items, name)
        if existing_index is None:
            return f"'{name}' is not on the list."
        existing_item = items[existing_index]
        if quantity is None or quantity >= existing_item.quantity:
            items.pop(existing_index)
            self._save_items(items)
            return f"Removed '{existing_item.name}' from the list."
        existing_item.quantity -= quantity
        self._save_items(items)
        return f"Reduced '{existing_item.name}' to {existing_item.quantity}."

    def set_quantity(self, name: str, quantity: int, note: str | None = None) -> GroceryItem:
        items = self.list_items()
        existing_index = self._find_item_index(items, name)
        if existing_index is not None:
            existing_item = items[existing_index]
            existing_item.quantity = quantity
            if note:
                existing_item.note = note
            updated_item = existing_item
        else:
            updated_item = GroceryItem(name=name, quantity=quantity, note=note)
            items.append(updated_item)
        self._save_items(items)
        return updated_item

    def clear(self) -> None:
        self._save_items([])
