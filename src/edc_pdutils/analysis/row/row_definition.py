import pandas as pd

from ..constants import N_WITH_ROW_PROP, STATISTICS
from ..styler import StylerError


class RowDefinition:
    def __init__(
        self,
        title: str | None = None,
        label: str = None,
        colname: str | None = None,
        condition: pd.Series = None,
        columns: dict[str, tuple[str, int]] = None,
        drop: bool | None = None,
    ):
        self.title = title or ""
        self.label = label
        self.colname = colname
        self.condition = condition  # condition to filter DF
        self.drop = False if drop is None else drop  # drop index of previous row numerator
        self.columns = columns or {"All": (N_WITH_ROW_PROP, 2)}
        for col, style_info in self.columns.items():
            style, _ = style_info
            if style not in STATISTICS:
                raise StylerError(f"Unknown statistic. Got `{style}` for column `{col}`.")
