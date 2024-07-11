import pandas as pd

from edc_pdutils.analysis import Row, default_columns


class Table:

    statistic_col = "Statistics"
    female_col = "F"
    male_col = "M"
    all_col = "All"
    n_sublabel = "n"
    grand_total_col = "tot"

    def __init__(
        self,
        main_df: pd.DataFrame = None,
        label: str | None = None,
        columns: list[str] | None = None,
        show_ncol_perc: bool | None = None,
        show_range: bool | None = None,
        round_int: int | None = None,
    ):

        self._row_zero: Row | None = None
        self.main_df = main_df
        self.label = label
        self.round_int = round_int or 2
        self.columns = default_columns or columns
        self.show_ncol_perc = show_ncol_perc
        self.show_range = show_range
        self.table_df = pd.DataFrame(columns=self.columns)

        self.build_table_df()

        # format string cols
        self.table_df[self.female_col] = self.table_df.apply(
            lambda x: self.format_f_col(x), axis=1
        )
        self.table_df[self.male_col] = self.table_df.apply(
            lambda x: self.format_m_col(x), axis=1
        )
        self.table_df[self.all_col] = self.table_df.apply(
            lambda x: self.format_all_col(x), axis=1
        )

    @property
    def row_zero(self) -> Row:
        if not self._row_zero:
            self._row_zero = Row(
                self.main_df,
                self.main_df,
                label=self.label,
                statistic=self.n_sublabel,
                columns=self.columns,
                use_rowperc=True,
            )
        return self._row_zero

    def build_table_df(self):
        """Override to build your table DF"""
        self.table_df.loc[0] = self.row_zero.values()

    @property
    def formatted_df(self):
        """Return DF with first 5 columns"""
        return self.table_df.iloc[:, :5]

    def format_f_col(self, x):
        if self.show_range:
            return f"{x.fnum} ({x.fmin}, {x.fmax})"
        elif pd.notna(x.q25):
            return (
                f"{round(x.fq50, self.round_int)} "
                "({round(x.fq25, self.round_int)},{round(x.fq75, self.round_int)})"
            )
        elif x[self.statistic_col] == self.n_sublabel:
            perc = f"({round(x.f_prop*100, self.round_int)}%)" if self.show_ncol_perc else ""
            return f"{x.fnum} {perc}"
        return f"{x.fnum} ({round(x.fnum/self.row_zero.f.total * 100, 1)}%)"

    def format_m_col(self, x):
        if self.show_range:
            return f"{x.mnum} ({x.mmin}, {x.mmax})"
        elif pd.notna(x.q25):
            return (
                f"{round(x.mq50, self.round_int)} "
                "({round(x.mq25, self.round_int)},{round(x.mq75, self.round_int)})"
            )
        elif x[self.statistic_col] == self.n_sublabel:
            perc = f"({round(x.m_prop*100, self.round_int)}%)" if self.show_ncol_perc else ""
            return f"{x.mnum} {perc}"
        return f"{x.mnum} ({round(x.mnum/self.row_zero.m.total * 100, 1)}%)"

    def format_all_col(self, x):
        if self.show_range:
            return f"{x.tot} ({x.min}, {x.max})"
        elif pd.notna(x.q25):
            return (
                f"{round(x.q50, self.round_int)} "
                "({round(x.q25, self.round_int)},{round(x.q75, self.round_int)})"
            )
        elif x[self.statistic_col] == self.n_sublabel:
            return f"{x.tot}"
        return f"{x.tot} ({round(x.tot/self.table_df.loc[0][self.grand_total_col] * 100, 1)}%)"
