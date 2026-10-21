"""Data model for a single expense."""

from dataclasses import dataclass
from datetime import date

# Categories the app knows about. Later, the ML model will learn to predict these.
CATEGORIES = ["food", "transport", "housing", "entertainment", "shopping", "health", "other"]


@dataclass
class Expense:
    """One expense entry.

    A dataclass automatically creates __init__, __repr__ and __eq__ for us,
    so we only describe the fields.
    """

    amount: float
    category: str
    description: str
    date: date

    def __post_init__(self) -> None:
        # Runs right after __init__: validate the data so a bad Expense can never exist.
        if self.amount <= 0:
            raise ValueError("Amount must be greater than 0.")
        self.category = self.category.strip().lower()
        if self.category not in CATEGORIES:
            raise ValueError(f"Unknown category '{self.category}'. Choose from: {', '.join(CATEGORIES)}")
        self.description = self.description.strip()

    def to_dict(self) -> dict:
        """Convert to a plain dict (used when saving to CSV)."""
        return {
            "amount": f"{self.amount:.2f}",
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat(),
        }

    @classmethod
    def from_dict(cls, row: dict) -> "Expense":
        """Build an Expense from a dict (used when loading from CSV)."""
        return cls(
            amount=float(row["amount"]),
            category=row["category"],
            description=row["description"],
            date=date.fromisoformat(row["date"]),
        )
