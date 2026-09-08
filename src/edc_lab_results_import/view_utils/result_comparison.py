from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from edc_lab_results.utils import get_decimal_places, get_utest_ids

from ..comparison_rules import add_comparison_columns
from ..constants import DIFFERS, NOT_COMPARED

if TYPE_CHECKING:
    from ..models import Result

__all__ = ["ResultComparison", "ResultComparisonRow"]


@dataclass
class ResultComparisonRow:
    """Compares one imported `Result` row with the matching fields on
    the result CRF.

    The comparison itself is not made here. `ResultComparison` runs the
    rows through `add_comparison_columns`, the same rule
    `get_df_result_comparison` uses trial-wide, and this reads the
    result off `data`. Nothing is written, this is for information only.

    Value, units and the abnormal flag are compared separately, so a
    row that agrees on the value but not on the units still reads as a
    difference.
    """

    result: Result
    model_obj: Any
    data: pd.Series

    @property
    def utest_id(self) -> str:
        return self.result.utestid

    @property
    def crf_value(self) -> Decimal | None:
        """Return the value as the CRF stores it, for display.

        `comparable_value` is the float the comparison was made on.
        """
        return getattr(self.model_obj, f"{self.utest_id}_value", None)

    @property
    def crf_units(self) -> str:
        return getattr(self.model_obj, f"{self.utest_id}_units", None) or ""

    @property
    def crf_abnormal(self) -> str:
        return getattr(self.model_obj, f"{self.utest_id}_abnormal", None) or ""

    @property
    def units(self) -> str:
        return self.result.units or ""

    @property
    def abnormal(self) -> str:
        """Return the abnormal flag implied by the lab's `flag`."""
        return self._as_str("abnormal")

    @property
    def comparable_value(self) -> float | None:
        """Return the imported value in the units used by the CRF.

        Returns None where the two cannot be expressed in the same
        units, in which case the value is not compared. The units
        difference is reported on its own.
        """
        value = self.data["comparable_value"]
        return None if pd.isna(value) else float(value)

    @property
    def value_status(self) -> str:
        return self._as_str("value_status")

    @property
    def units_status(self) -> str:
        return self._as_str("units_status")

    @property
    def abnormal_status(self) -> str:
        return self._as_str("abnormal_status")

    @property
    def differs(self) -> bool:
        return DIFFERS in (self.value_status, self.units_status, self.abnormal_status)

    @property
    def value_differs(self) -> bool:
        return self.value_status == DIFFERS

    @property
    def value_not_compared(self) -> bool:
        return self.value_status == NOT_COMPARED

    @property
    def units_differs(self) -> bool:
        return self.units_status == DIFFERS

    @property
    def abnormal_differs(self) -> bool:
        return self.abnormal_status == DIFFERS

    @property
    def abnormal_not_compared(self) -> bool:
        return self.abnormal_status == NOT_COMPARED

    def _as_str(self, column: str) -> str:
        value = self.data[column]
        return "" if pd.isna(value) else str(value)


@dataclass
class ResultComparison:
    """Compares the imported results of one result set with the result
    CRF they were, or are to be, transcribed onto.

    Only utest ids on the CRF are compared. Imported results with no
    field on the CRF are left out, as are CRF fields with no imported
    result. See `ResultSearchView.get_group_key` for the result set,
    and `get_df_result_comparison` for the trial-wide view, which does
    include the CRF fields with no imported result.
    """

    model_obj: Any
    results: list[Result]
    group_key: str = ""
    rows: list[ResultComparisonRow] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        utest_ids = get_utest_ids(self.model_obj._meta.model)
        results = [result for result in self.results if result.utestid in utest_ids]
        if not results:
            self.rows = []
            return
        df = add_comparison_columns(self.get_dataframe(results))
        self.rows = [
            ResultComparisonRow(result=result, model_obj=self.model_obj, data=df.iloc[index])
            for index, result in enumerate(results)
        ]

    def get_dataframe(self, results: list[Result]) -> pd.DataFrame:
        """Return one row per result in the columns the rule reads."""
        decimal_places = get_decimal_places(self.model_obj._meta.model)
        return pd.DataFrame(
            [
                dict(
                    has_import=True,
                    crf_value=as_float(
                        getattr(self.model_obj, f"{result.utestid}_value", None)
                    ),
                    crf_units=getattr(self.model_obj, f"{result.utestid}_units", None) or "",
                    crf_abnormal=getattr(self.model_obj, f"{result.utestid}_abnormal", None)
                    or "",
                    decimal_places=decimal_places.get(result.utestid),
                    result_value=as_float(result.result_value),
                    units=result.units or "",
                    converted_result_value=as_float(result.converted_result_value),
                    converted_units=result.converted_units or "",
                    flag=result.flag or "",
                )
                for result in results
            ]
        )

    @property
    def verbose_name(self) -> str:
        return self.model_obj._meta.verbose_name


def as_float(value: Decimal | None) -> float:
    return np.nan if value is None else float(value)
