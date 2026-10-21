"""Tests for Stage 2 (analysis, charts, sample data)."""

from datetime import date

from expense_tracker.analysis import ExpenseAnalyzer
from expense_tracker.charts import ChartMaker
from expense_tracker.models import CATEGORIES, Expense
from expense_tracker.sample_data import generate

EXPENSES = [
    Expense(10, "food", "Coffee", date(2026, 9, 1)),      # Tuesday
    Expense(30, "food", "Groceries", date(2026, 9, 10)),
    Expense(60, "transport", "Train", date(2026, 10, 1)),
]


def test_summary():
    s = ExpenseAnalyzer(EXPENSES).summary()
    assert s["total"] == 100
    assert s["count"] == 3
    assert s["average_expense"] == 33.33
    assert s["average_per_day"] == round(100 / 31, 2)  # Sep 1 -> Oct 1 is 31 days


def test_summary_empty():
    assert ExpenseAnalyzer([]).summary()["total"] == 0.0


def test_by_category():
    result = ExpenseAnalyzer(EXPENSES).by_category()
    assert list(result.index) == ["transport", "food"]
    assert result.loc["food", "total"] == 40
    assert result.loc["food", "count"] == 2
    assert result.loc["transport", "share_pct"] == 60.0


def test_monthly_change():
    result = ExpenseAnalyzer(EXPENSES).monthly()
    assert result.loc["2026-09", "total"] == 40
    assert result.loc["2026-10", "change_pct"] == 50.0  # 40 -> 60


def test_largest():
    assert ExpenseAnalyzer(EXPENSES).largest(1).loc[0, "description"] == "Train"


def test_by_weekday_has_all_days():
    result = ExpenseAnalyzer(EXPENSES).by_weekday()
    assert len(result) == 7
    assert result["Tuesday"] == 10


def test_charts_are_created(tmp_path):
    paths = ChartMaker(ExpenseAnalyzer(EXPENSES), tmp_path).make_all()
    assert len(paths) == 3
    assert all(p.exists() and p.stat().st_size > 0 for p in paths)


def test_no_charts_when_empty(tmp_path):
    assert ChartMaker(ExpenseAnalyzer([]), tmp_path).make_all() == []


def test_sample_data_is_valid_and_reproducible():
    a, b = generate(months=2, end=date(2026, 10, 1)), generate(months=2, end=date(2026, 10, 1))
    assert a == b  # same seed -> same data
    assert {e.category for e in a} <= set(CATEGORIES)
    assert all(e.date <= date(2026, 10, 1) for e in a)
