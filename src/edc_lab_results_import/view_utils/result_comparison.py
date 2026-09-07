from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Any

from clinicedc_constants import NO, YES

from edc_lab_results.utils import get_utest_ids

from ..constants import ABNORMAL_FLAGS, DIFFERS, MATCH, NOT_COMPARED

if TYPE_CHECKING:
    from ..models import Result

__all__ = ["ResultComparison", "ResultComparisonRow"]


@dataclass
class ResultComparisonRow:
    """Compares one imported `Result` row with the matching fields on
    the result CRF.

    Value, units and the abnormal flag are compared separately, so a
    row that agrees on the value but not on the units still reads as a
    difference. Nothing is written, this is for information only.
    """

    result: Result
    model_obj: Any

    @property
    def utest_id(self) -> str:
        return self.result.utestid

    @property
    def crf_value(self) -> Decimal | None:
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
        """Return the abnormal flag implied by the lab's `flag`.

        A blank flag means the lab did not call the value abnormal.
        A flag that is neither blank nor recognized is not interpreted.
        """
        flag = (self.result.flag or "").strip().lower()
        if not flag:
            return NO
        return YES if flag in ABNORMAL_FLAGS else ""

    @property
    def comparable_value(self) -> Decimal | None:
        """Return the imported value in the units used by the CRF.

        Returns None where the two cannot be expressed in the same
        units, in which case the value is not compared. The units
        difference is reported on its own.
        """
        if self.units and self.units == self.crf_units:
            return self.result.result_value
        converted_units = self.result.converted_units or ""
        if converted_units and converted_units == self.crf_units:
            return self.result.converted_result_value
        return None

    @property
    def value_status(self) -> str:
        if self.crf_value is None and self.result.result_value is None:
            return MATCH
        if self.crf_value is None or self.result.result_value is None:
            return DIFFERS
        value = self.comparable_value
        if value is None:
            return NOT_COMPARED
        return MATCH if self.quantize(value) == self.quantize(self.crf_value) else DIFFERS

    @property
    def units_status(self) -> str:
        return MATCH if self.units == self.crf_units else DIFFERS

    @property
    def abnormal_status(self) -> str:
        if not self.abnormal:
            return NOT_COMPARED
        return MATCH if self.abnormal == self.crf_abnormal else DIFFERS

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

    def quantize(self, value: Decimal) -> Decimal:
        """Return the value at the precision stored by the CRF.

        The imported value carries more decimal places than most CRF
        fields, so 13.4000 and 13.4 must not read as a difference.
        """
        try:
            decimal_places = self.model_obj._meta.get_field(
                f"{self.utest_id}_value"
            ).decimal_places
        except AttributeError:
            return value
        if decimal_places is None:
            return value
        return value.quantize(Decimal(1).scaleb(-decimal_places), rounding=ROUND_HALF_UP)


@dataclass
class ResultComparison:
    """Compares the imported results of one result set with the result
    CRF they were, or are to be, transcribed onto.

    Only utest ids on the CRF are compared. Imported results with no
    field on the CRF are left out, as are CRF fields with no imported
    result. See `ResultSearchView.get_group_key` for the result set.
    """

    model_obj: Any
    results: list[Result]
    group_key: str = ""
    rows: list[ResultComparisonRow] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        utest_ids = get_utest_ids(self.model_obj._meta.model)
        self.rows = [
            ResultComparisonRow(result=result, model_obj=self.model_obj)
            for result in self.results
            if result.utestid in utest_ids
        ]

    @property
    def verbose_name(self) -> str:
        return self.model_obj._meta.verbose_name
