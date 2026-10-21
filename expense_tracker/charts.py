"""Stage 2: charts with matplotlib, saved as PNG files."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to files instead of opening a window (works everywhere, incl. servers)
import matplotlib.pyplot as plt

from expense_tracker.analysis import ExpenseAnalyzer

COLOR = "#2a7ab0"


class ChartMaker:
    def __init__(self, analyzer: ExpenseAnalyzer, output_dir: str | Path = "charts") -> None:
        self.analyzer = analyzer
        self.output_dir = Path(output_dir)

    def make_all(self) -> list[Path]:
        """Create every chart and return the paths of the saved files."""
        if self.analyzer.is_empty:
            return []
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return [self.category_chart(), self.monthly_chart(), self.weekday_chart()]

    def category_chart(self) -> Path:
        data = self.analyzer.by_category()["total"].sort_values()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(data.index, data.values, color=COLOR)
        for i, value in enumerate(data.values):
            ax.text(value, i, f" {value:,.0f}", va="center")
        ax.set_title("Spending by category")
        ax.set_xlabel("Total spent")
        return self._save(fig, "by_category.png")

    def monthly_chart(self) -> Path:
        data = self.analyzer.monthly()["total"]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(data.index, data.values, marker="o", color=COLOR, linewidth=2)
        ax.set_title("Spending per month")
        ax.set_ylabel("Total spent")
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", alpha=0.3)
        return self._save(fig, "monthly.png")

    def weekday_chart(self) -> Path:
        data = self.analyzer.by_weekday()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar([d[:3] for d in data.index], data.values, color=COLOR)
        ax.set_title("Spending by day of the week")
        ax.set_ylabel("Total spent")
        return self._save(fig, "by_weekday.png")

    def _save(self, fig, filename: str) -> Path:
        for side in ("top", "right"):
            fig.axes[0].spines[side].set_visible(False)
        fig.tight_layout()
        path = self.output_dir / filename
        fig.savefig(path, dpi=120)
        plt.close(fig)  # free memory
        return path
