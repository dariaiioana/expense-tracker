"""Saving and loading expenses.

Storage is kept separate from the rest of the app on purpose: in Stage 3 we
replace CSVStorage with a database, and nothing else in the code has to change.
"""

import csv
from pathlib import Path

from expense_tracker.models import Expense

FIELDNAMES = ["amount", "category", "description", "date"]


class CSVStorage:
    """Stores expenses in a CSV file."""

    def __init__(self, path: str | Path = "expenses.csv") -> None:
        self.path = Path(path)

    def load(self) -> list[Expense]:
        """Read all expenses from the file. Returns [] if the file doesn't exist yet."""
        if not self.path.exists():
            return []
        with self.path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [Expense.from_dict(row) for row in reader]

    def save(self, expenses: list[Expense]) -> None:
        """Write all expenses to the file (overwrites it)."""
        with self.path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for expense in expenses:
                writer.writerow(expense.to_dict())
