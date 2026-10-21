"""Tests. Run with:  pytest"""

from datetime import date

import pytest

from expense_tracker.models import Expense
from expense_tracker.storage import CSVStorage
from expense_tracker.tracker import ExpenseTracker


@pytest.fixture
def tracker(tmp_path):
    # tmp_path is a temporary folder pytest creates for each test, so tests never touch your real data.
    return ExpenseTracker(CSVStorage(tmp_path / "test.csv"))


def test_add_expense(tracker):
    tracker.add(12.5, "food", "Lunch", date(2026, 10, 1))
    assert len(tracker.all()) == 1
    assert tracker.total() == 12.5


def test_rejects_negative_amount(tracker):
    with pytest.raises(ValueError):
        tracker.add(-5, "food", "Oops")


def test_rejects_unknown_category(tracker):
    with pytest.raises(ValueError):
        tracker.add(10, "pizza", "Not a category")


def test_category_is_normalized():
    e = Expense(10, "  FOOD ", "x", date(2026, 1, 1))
    assert e.category == "food"


def test_totals_by_category(tracker):
    tracker.add(10, "food", "a", date(2026, 10, 1))
    tracker.add(5, "food", "b", date(2026, 10, 2))
    tracker.add(20, "transport", "c", date(2026, 10, 3))
    assert tracker.totals_by_category() == {"transport": 20.0, "food": 15.0}


def test_totals_by_month(tracker):
    tracker.add(10, "food", "a", date(2026, 9, 30))
    tracker.add(5, "food", "b", date(2026, 10, 1))
    assert tracker.totals_by_month() == {"2026-09": 10.0, "2026-10": 5.0}


def test_data_persists_between_runs(tmp_path):
    path = tmp_path / "data.csv"
    ExpenseTracker(CSVStorage(path)).add(7, "health", "Pharmacy", date(2026, 10, 5))
    reloaded = ExpenseTracker(CSVStorage(path))  # simulates restarting the app
    assert reloaded.total() == 7
    assert reloaded.all()[0].description == "Pharmacy"


def test_all_is_sorted_newest_first(tracker):
    tracker.add(1, "other", "old", date(2026, 1, 1))
    tracker.add(1, "other", "new", date(2026, 6, 1))
    assert [e.description for e in tracker.all()] == ["new", "old"]
