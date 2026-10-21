"""Command-line interface: the only file that uses input() and print()."""

import argparse
from datetime import date

from expense_tracker.analysis import ExpenseAnalyzer
from expense_tracker.charts import ChartMaker
from expense_tracker.models import CATEGORIES
from expense_tracker.storage import CSVStorage
from expense_tracker.tracker import ExpenseTracker

MENU = """
=== Expense Tracker ===
1) Add expense
2) List expenses
3) Totals by category
4) Totals by month
5) Analysis report
6) Generate charts
7) Quit
"""


class CLI:
    def __init__(self, tracker: ExpenseTracker) -> None:
        self.tracker = tracker
        # Maps a menu choice to the method that handles it (cleaner than a long if/elif chain).
        self.actions = {
            "1": self.add_expense,
            "2": self.list_expenses,
            "3": self.show_category_totals,
            "4": self.show_month_totals,
            "5": self.show_report,
            "6": self.make_charts,
        }

    def run(self) -> None:
        while True:
            print(MENU)
            choice = input("Choose an option: ").strip()
            if choice == "7":
                print("Bye!")
                break
            action = self.actions.get(choice)
            if action:
                action()
            else:
                print("Invalid option, try again.")

    # ---------- menu actions ----------

    def add_expense(self) -> None:
        amount = self._ask_amount()
        category = self._ask_category()
        description = input("Description: ").strip()
        when = self._ask_date()
        expense = self.tracker.add(amount, category, description, when)
        print(f"Saved: {expense.amount:.2f} for {expense.category} on {expense.date}")

    def list_expenses(self) -> None:
        expenses = self.tracker.all()
        if not expenses:
            print("No expenses yet.")
            return
        print(f"\n{'Date':<12}{'Category':<15}{'Amount':>10}  Description")
        print("-" * 55)
        for e in expenses:
            print(f"{e.date.isoformat():<12}{e.category:<15}{e.amount:>10.2f}  {e.description}")
        print("-" * 55)
        print(f"{'Total':<27}{self.tracker.total():>10.2f}")

    def show_category_totals(self) -> None:
        self._print_totals(self.tracker.totals_by_category(), "Category")

    def show_month_totals(self) -> None:
        self._print_totals(self.tracker.totals_by_month(), "Month")

    def show_report(self) -> None:
        analyzer = ExpenseAnalyzer(self.tracker.all())
        if analyzer.is_empty:
            print("No expenses yet.")
            return
        s = analyzer.summary()
        print("\n=== Summary ===")
        print(f"Total spent:      {s['total']:.2f}")
        print(f"Expenses:         {s['count']}")
        print(f"Average expense:  {s['average_expense']:.2f}")
        print(f"Average per day:  {s['average_per_day']:.2f}")
        print("\n=== By category ===")
        print(analyzer.by_category().to_string())
        print("\n=== By month (change vs previous month, %) ===")
        print(analyzer.monthly().to_string())
        print("\n=== 5 largest expenses ===")
        print(analyzer.largest(5)[["date", "category", "amount", "description"]].to_string(index=False))

    def make_charts(self) -> None:
        paths = ChartMaker(ExpenseAnalyzer(self.tracker.all())).make_all()
        if not paths:
            print("No expenses yet, nothing to chart.")
            return
        print("Charts saved:")
        for path in paths:
            print(f"  {path}")

    # ---------- input helpers (keep asking until the input is valid) ----------

    def _ask_amount(self) -> float:
        while True:
            try:
                amount = float(input("Amount: ").replace(",", "."))
                if amount > 0:
                    return amount
                print("Amount must be greater than 0.")
            except ValueError:
                print("Please enter a number, e.g. 12.50")

    def _ask_category(self) -> str:
        print("Categories: " + ", ".join(CATEGORIES))
        while True:
            category = input("Category: ").strip().lower()
            if category in CATEGORIES:
                return category
            print("Unknown category, pick one from the list.")

    def _ask_date(self) -> date:
        while True:
            raw = input("Date (YYYY-MM-DD, leave empty for today): ").strip()
            if not raw:
                return date.today()
            try:
                return date.fromisoformat(raw)
            except ValueError:
                print("Invalid date. Use the format 2026-10-21")

    @staticmethod
    def _print_totals(totals: dict[str, float], label: str) -> None:
        if not totals:
            print("No expenses yet.")
            return
        print(f"\n{label:<15}{'Total':>10}")
        print("-" * 25)
        for key, amount in totals.items():
            print(f"{key:<15}{amount:>10.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Track and analyze your expenses.")
    parser.add_argument("--data", default="expenses.csv", help="CSV file to use (default: expenses.csv)")
    args = parser.parse_args()
    tracker = ExpenseTracker(CSVStorage(args.data))
    CLI(tracker).run()
