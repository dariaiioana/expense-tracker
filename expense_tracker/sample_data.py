"""Generate realistic fake expenses for demos and screenshots.

Run:  python -m expense_tracker.sample_data
This writes sample_expenses.csv. Later (Stage 4) this data also helps train
the ML model, because each category uses typical descriptions.
"""

import random
from datetime import date, timedelta

from expense_tracker.models import Expense
from expense_tracker.storage import CSVStorage

# category -> (possible descriptions, min amount, max amount, roughly how many per month)
TEMPLATES = {
    "food": (["Groceries Lidl", "Groceries Kaufland", "Lunch at canteen", "Pizza delivery", "Coffee", "Bakery", "Sushi dinner"], 5, 80, 18),
    "transport": (["Bus ticket", "Metro pass", "Uber ride", "Bolt ride", "Fuel", "Train ticket"], 3, 60, 8),
    "housing": (["Rent", "Electricity bill", "Internet bill", "Water bill"], 40, 400, 3),
    "entertainment": (["Cinema", "Netflix subscription", "Spotify", "Concert ticket", "Bowling", "Video game"], 8, 120, 4),
    "shopping": (["Clothes", "Shoes", "Phone case", "Books", "Headphones", "Backpack"], 15, 250, 3),
    "health": (["Pharmacy", "Gym membership", "Vitamins", "Dentist"], 10, 200, 2),
    "other": (["Gift", "Haircut", "Laundry", "Phone top-up"], 5, 100, 2),
}


def generate(months: int = 6, end: date | None = None, seed: int = 42) -> list[Expense]:
    """Create fake expenses spread over the last `months` months."""
    rng = random.Random(seed)  # fixed seed -> same data every run (reproducible)
    end = end or date.today()
    # Start on the 1st of the month, `months - 1` months before the end month.
    month_index = end.year * 12 + end.month - 1 - (months - 1)
    start = date(month_index // 12, month_index % 12 + 1, 1)
    expenses = []
    for category, (descriptions, low, high, per_month) in TEMPLATES.items():
        for _ in range(per_month * months):
            when = start + timedelta(days=rng.randint(0, (end - start).days))
            amount = round(rng.uniform(low, high), 2)
            expenses.append(Expense(amount, category, rng.choice(descriptions), when))
    return sorted(expenses, key=lambda e: e.date)


if __name__ == "__main__":
    data = generate()
    CSVStorage("sample_expenses.csv").save(data)
    print(f"Wrote {len(data)} sample expenses to sample_expenses.csv")
