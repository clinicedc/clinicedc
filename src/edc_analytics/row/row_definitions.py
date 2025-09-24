from collections.abc import Iterable

from .row_definition import RowDefinition
from .row_statistics import RowStatistics
from .row_statistics_with_gender import RowStatisticsWithGender


class RowDefinitions:
    """Collection of RowDefinitions"""

    def __init__(
        self,
        colname: str = None,
        row_statistics_cls: RowStatistics | RowStatisticsWithGender = None,
        reverse_rows: bool = False,
    ):
        self.definitions: list[RowDefinition] = []
        self.row_statistics_cls = row_statistics_cls
        self.colname = colname
        self.reverse_rows = reverse_rows

    def add(self, row_definition: RowDefinition):
        self.definitions.append(row_definition)

    def extend(self, row_definition: list[RowDefinition]):
        self.definitions.extend(row_definition)

    def reverse(self):
        self.definitions.reverse()

    def __iter__(self) -> Iterable[RowDefinition]:
        return iter(self.definitions)
