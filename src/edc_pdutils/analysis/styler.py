from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import (
    MEAN_95CI,
    MEAN_RANGE,
    MEAN_SD,
    MEDIAN_IQR,
    MEDIAN_RANGE,
    N_MEAN,
    N_ONLY,
    N_RANGE,
    N_WITH_COL_PROP,
    N_WITH_ROW_PROP,
    STATISTICS,
)

if TYPE_CHECKING:
    from .row import RowStatistics


class StylerError(Exception):
    pass


class Styler:
    def __init__(
        self, style: str = None, statistics: RowStatistics = None, places: int | None = None
    ):
        self.style = style
        self.row = statistics
        self.places = places or 2
        if style not in STATISTICS:
            raise StylerError(f"Unknown style. Got `{style}`.")

    @property
    def value(self):
        """Make sure values are numerics first!

        For example, when preparing the dataframe convert values to
        numerics:
            df[cols] = df[cols].apply(pd.to_numeric)
        """
        col_value = "no style"
        if self.style == N_WITH_ROW_PROP:
            col_value = f"{self.row.count} ({round(self.row.rowprop * 100, self.places)}%)"
        elif self.style == N_ONLY:
            col_value = f"{self.row.count}"
        elif self.style == N_WITH_COL_PROP:
            col_value = f"{self.row.count} ({round(self.row.colprop * 100, self.places)}%)"
        elif self.style == N_RANGE:
            col_value = f"{self.row.count} ({self.row.min}, {self.row.max})"
        elif self.style == N_MEAN:
            col_value = f"{round(self.row.mean, self.places)}"
        elif self.style == MEDIAN_IQR:
            col_value = (
                f"{round(self.row.q50, self.places)} "
                f"({round(self.row.q25, self.places)},{round(self.row.q75, self.places)})"
            )
        elif self.style == MEDIAN_RANGE:
            col_value = (
                f"{round(self.row.q50, self.places)} "
                f"({round(self.row.min, self.places)}, {round(self.row.max, self.places)})"
            )
        elif self.style == MEAN_RANGE:
            col_value = (
                f"{round(self.row.mean, self.places)} "
                f"({round(self.row.min, self.places)}, {round(self.row.max, self.places)})"
            )
        elif self.style == MEAN_SD:
            col_value = (
                f"{round(self.row.mean, self.places)} ({round(self.row.sd, self.places)})"
            )
        elif self.style == MEAN_95CI:
            col_value = (
                f"{round(self.row.mean, self.places)} "
                f"({round(self.row.ci95l, self.places)}, {round(self.row.ci95h, self.places)})"
            )
        return col_value
