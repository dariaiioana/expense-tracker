"""Stage 2: spending analysis with pandas.

ExpenseAnalyzer takes a list of Expense objects and answers questions about
them. Like ExpenseTracker, it never prints or asks for input, so it's easy to
test and the web API (Stage 3) can reuse it.
"""

import pandas as pd

from expense_tracker.models import Expense


class ExpenseAnalyzer:
    def __init__(self, expenses: list[Expense]) -> None:
        # One row per expense; columns: amount, category, description, date.
        self.df = pd.DataFrame(
            [{"amount": e.amount, "category": e.category, "description": e.description, "date": e.date} for e in expenses],
            columns=["amount", "category", "description", "date"],
        )
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["amount"] = self.df["amount"].astype(float)

    @property
    def is_empty(self) -> bool:
        return self.df.empty

    def summary(self) -> dict:
        """Headline numbers: total, count, average expense, average per day."""
        if self.is_empty:
            return {"total": 0.0, "count": 0, "average_expense": 0.0, "average_per_day": 0.0}
        days = (self.df["date"].max() - self.df["date"].min()).days + 1
        total = self.df["amount"].sum()
        return {
            "total": round(float(total), 2),
            "count": int(len(self.df)),
            "average_expense": round(float(self.df["amount"].mean()), 2),
            "average_per_day": round(float(total / days), 2),
        }

    def by_category(self) -> pd.DataFrame:
        """Total, count and share (%) per category, biggest first."""
        grouped = self.df.groupby("category")["amount"].agg(total="sum", count="count")
        grouped["share_pct"] = (grouped["total"] / grouped["total"].sum() * 100).round(1)
        grouped["total"] = grouped["total"].round(2)
        return grouped.sort_values("total", ascending=False)

    def monthly(self) -> pd.DataFrame:
        """Total per month and the % change from the previous month."""
        monthly = self.df.groupby(self.df["date"].dt.to_period("M"))["amount"].sum().to_frame("total")
        monthly["change_pct"] = (monthly["total"].pct_change() * 100).round(1)
        monthly["total"] = monthly["total"].round(2)
        monthly.index = monthly.index.astype(str)
        return monthly

    def largest(self, n: int = 5) -> pd.DataFrame:
        """The n biggest single expenses."""
        return self.df.nlargest(n, "amount").reset_index(drop=True)

    def by_weekday(self) -> pd.Series:
        """Total spent per day of the week, Monday first."""
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return self.df.groupby(self.df["date"].dt.day_name())["amount"].sum().reindex(order, fill_value=0.0).round(2)
