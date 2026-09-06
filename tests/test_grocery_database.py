from pathlib import Path

import pytest

from app.grocery_database import GroceryDatabase


@pytest.fixture
def grocery_database(tmp_path: Path) -> GroceryDatabase:
    markdown_file_path = tmp_path / "groceries.md"
    markdown_file_path.write_text("# Groceries List\n\n## Items\n", encoding="utf-8")
    return GroceryDatabase(markdown_file_path)


def test_add_item_creates_new_entry(grocery_database: GroceryDatabase):
    grocery_database.add_item("Milk", quantity=2, note="3%")

    items = grocery_database.list_items()

    assert len(items) == 1
    assert items[0].name == "Milk"
    assert items[0].quantity == 2
    assert items[0].note == "3%"


def test_add_item_increments_existing_entry_case_insensitively(grocery_database: GroceryDatabase):
    grocery_database.add_item("Milk", quantity=2)
    grocery_database.add_item("milk", quantity=3)

    items = grocery_database.list_items()

    assert len(items) == 1
    assert items[0].quantity == 5


def test_remove_item_without_quantity_removes_entirely(grocery_database: GroceryDatabase):
    grocery_database.add_item("Eggs", quantity=12)

    grocery_database.remove_item("Eggs")

    assert grocery_database.list_items() == []


def test_remove_item_with_quantity_reduces_count(grocery_database: GroceryDatabase):
    grocery_database.add_item("Eggs", quantity=12)

    grocery_database.remove_item("Eggs", quantity=5)

    items = grocery_database.list_items()
    assert len(items) == 1
    assert items[0].quantity == 7


def test_set_quantity_overrides_existing_value(grocery_database: GroceryDatabase):
    grocery_database.add_item("Bread", quantity=1)

    grocery_database.set_quantity("Bread", quantity=4)

    assert grocery_database.list_items()[0].quantity == 4


def test_clear_empties_the_list(grocery_database: GroceryDatabase):
    grocery_database.add_item("Bread", quantity=1)
    grocery_database.add_item("Milk", quantity=2)

    grocery_database.clear()

    assert grocery_database.list_items() == []
