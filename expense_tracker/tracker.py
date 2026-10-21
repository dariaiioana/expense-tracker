"""Business logic: everything the app can *do* with expenses.

This class knows nothing about the terminal or input(). That makes it easy to
test, and later the web API (Stage 3) will call these same methods.
"""

from collections import defaultdict
from datetime import date

from expense_tracker.models import Expense
from expense_tracker.storage import CSVStorage


class ExpenseTracker:
    def __init__(self, storage: CSVStorage) -> None:
        self.storage = storage
        self.expenses: list[Expense] = storage.load()

    def add(self, amount: float, category: str, description: str, when: date | None = None) -> Expense:
        """Create, store and return a new expense. Date defaults to today."""
        expense = Expense(amount, category, description, when or date.today())
        self.expenses.append(expense)
        self.storage.save(self.expenses)
        return expense

    def all(self) -> list[Expense]:
        """All expenses, newest first."""
        return sorted(self.expenses, key=lambda e: e.date, reverse=True)

    def total(self) -> float:
        return round(sum(e.amount for e in self.expenses), 2)

    def totals_by_category(self) -> dict[str, float]:
        """e.g. {"food": 120.5, "transport": 40.0}, biggest first."""
        totals: dict[str, float] = defaultdict(float)
        for e in self.expenses:
            totals[e.category] += e.amount
        return {cat: round(amt, 2) for cat, amt in sorted(totals.items(), key=lambda x: x[1], reverse=True)}

    def totals_by_month(self) -> dict[str, float]:
        """e.g. {"2026-09": 300.0, "2026-10": 250.0}, oldest first."""
        totals: dict[str, float] = defaultdict(float)
        for e in self.expenses:
            totals[e.date.strftime("%Y-%m")] += e.amount
        return {month: round(amt, 2) for month, amt in sorted(totals.items())}
