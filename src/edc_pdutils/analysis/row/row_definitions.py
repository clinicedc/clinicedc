from .row_definition import RowDefinition
from .row_statistics import RowStatistics
from .row_statistics_with_gender import RowStatisticsWithGender


class RowDefinitions:
    """Collection of RowDefinitions"""

    def __init__(
        self,
        colname: str = None,
        row_cls: RowStatistics | RowStatisticsWithGender = None,
        reverse_rows: bool = False,
    ):
        self.definitions: list[RowDefinition] = []
        self.row_cls = row_cls
        self.colname = colname
        self.reverse_rows = reverse_rows

    def add(self, row_definition: RowDefinition):
        self.definitions.append(row_definition)

    def reverse(self):
        self.definitions.reverse()
