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
    N_WITH_COL_PROP,
    N_WITH_ROW_PROP,
    STATISTICS,
)

if TYPE_CHECKING:
    from .row import RowStatistics


class StylerError(Exception):
    pass


class Styler:
    """A class to format statistics per the format label given."""

    def __init__(
        self,
        style: str = None,
        statistics: RowStatistics = None,
        places: int | None = None,
    ):
        self.style = style
        self.row = statistics
        self.places = places if places is not None else 2
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
            col_value = (
                f"{self.row.count} ("
                f"{round(self.row.rowprop * 100, self.places):.{self.places}f}%)"
            )
        elif self.style == N_ONLY:
            col_value = f"{self.row.count}"
        elif self.style == N_WITH_COL_PROP:
            col_value = (
                f"{self.row.count:.{self.places}f} "
                f"({round(self.row.colprop * 100, self.places):.{self.places}f}%)"
            )
        elif self.style == N_MEAN:
            col_value = f"{round(self.row.mean, self.places):.{self.places}f}"
        elif self.style == MEDIAN_IQR:
            col_value = (
                f"{round(self.row.q50, self.places):.{self.places}f} "
                f"({round(self.row.q25, self.places)},"
                f"{round(self.row.q75, self.places):.{self.places}f})"
            )
        elif self.style == MEDIAN_RANGE:
            col_value = (
                f"{round(self.row.q50, self.places):.{self.places}f} "
                f"({round(self.row.min, self.places):.{self.places}f}, "
                f"{round(self.row.max, self.places):.{self.places}f})"
            )
        elif self.style == MEAN_RANGE:
            col_value = (
                f"{round(self.row.mean, self.places):.{self.places}f} "
                f"({round(self.row.min, self.places):.{self.places}f}, "
                f"{round(self.row.max, self.places):.{self.places}f})"
            )
        elif self.style == MEAN_SD:
            col_value = (
                f"{round(self.row.mean, self.places):.{self.places}f} "
                f"({round(self.row.sd, self.places):.{self.places}f})"
            )
        elif self.style == MEAN_95CI:
            col_value = (
                f"{round(self.row.mean, self.places):.{self.places}f} "
                f"({round(self.row.ci95l, self.places):.{self.places}f}, "
                f"{round(self.row.ci95h, self.places):.{self.places}f})"
            )
        return col_value
