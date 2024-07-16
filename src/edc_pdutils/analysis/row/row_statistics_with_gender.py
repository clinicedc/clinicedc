import pandas as pd

from .row_statistics import RowStatistics


class RowStatisticsFemale(RowStatistics):
    def __init__(
        self,
        female_value: str = None,
        df_numerator: pd.DataFrame = None,
        df_denominator: pd.DataFrame = None,
        **kwargs,
    ):
        female_value = female_value or "Female"
        if not df_numerator.empty:
            df_numerator = df_numerator.loc[df_numerator["gender"] == female_value]
        super().__init__(
            df_numerator=df_numerator,
            df_denominator=df_denominator.loc[df_denominator["gender"] == female_value],
            **kwargs,
        )


class RowStatisticsMale(RowStatistics):
    def __init__(
        self,
        male_value: str = None,
        df_numerator: pd.DataFrame = None,
        df_denominator: pd.DataFrame = None,
        **kwargs,
    ):
        male_value = male_value or "Male"
        if not df_numerator.empty:
            df_numerator = df_numerator.loc[df_numerator["gender"] == male_value]
        super().__init__(
            df_numerator=df_numerator,
            df_denominator=df_denominator.loc[df_denominator["gender"] == male_value],
            **kwargs,
        )


class RowStatisticsWithGender(RowStatistics):
    def __init__(
        self,
        columns: dict[str, tuple[str, int]] = None,
        gender_values: dict[str, str] = None,
        df_all: pd.DataFrame = None,
        coltotal: float | int | None = None,
        **kwargs,
    ):
        """
        custom row for displaying with gender columns: F, M, All
        :param colname:
        :param df_numerator:
        :param df_denominator:
        :param df_all:
        :param columns: dict of {col: (style name, places)} where col
               is "F", "M" or "All"
        :param gender_values: dict of {gender_label: gender_value} where
               gender_label is "F" or "M"
        """

        female_style, female_places = columns["F"]
        male_style, male_places = columns["M"]
        all_style, all_places = columns["All"]

        gender_values = gender_values or {"M": "Male", "F": "Female"}
        female_value = gender_values["F"]
        male_value = gender_values["M"]

        super().__init__(
            places=all_places, style=all_style, df_all=df_all, coltotal=coltotal, **kwargs
        )

        self.m = RowStatisticsMale(
            male_value=male_value,
            places=male_places,
            style=male_style,
            coltotal=len(df_all[df_all["gender"] == male_value]),
            df_all=df_all,
            **kwargs,
        )
        self.f = RowStatisticsFemale(
            female_value=female_value,
            places=female_places,
            style=female_style,
            coltotal=len(df_all[df_all["gender"] == female_value]),
            df_all=df_all,
            **kwargs,
        )

    def values_list(self, style: str | None = None, places: int | None = None) -> list:
        values_list = super().values_list()
        return (
            list(self.formatted_cells().values())
            + self.f.values_list()
            + self.m.values_list()
            + values_list
        )

    def labels(self) -> list[str]:
        labels = super().labels()
        return (
            list(self.formatted_cells().keys())
            + [f"f{x}" for x in self.f.labels()]
            + [f"m{x}" for x in self.m.labels()]
            + labels
        )

    def row(self):
        return [self.formatted_cells()] + self.values_list()

    def formatted_cells(self) -> dict:
        formatted_cell = super().formatted_cell()
        return dict(
            F=self.f.formatted_cell(),
            M=self.m.formatted_cell(),
            All=formatted_cell,
        )
