from abc import ABC, abstractmethod
from typing import Optional

from django.db import models
from django.utils.html import format_html
from edc_constants.constants import NO, TBD, YES


class ScreeningEligibilityError(Exception):
    pass


class ScreeningEligibility(ABC):
    def __init__(
        self,
        model_obj: models.Model,
        allow_none: Optional[bool] = None,
    ):
        self.model_obj = model_obj
        self.eligible: Optional[str] = None
        self.reasons_ineligible: Optional[dict] = None
        self.allow_none = allow_none  # TODO: allow_none ??
        self.pre_assess_eligibility()
        self.assess_eligibility()
        if (
            not self.eligible
            or self.eligible not in [YES, NO, TBD]
            or self.reasons_ineligible is None
        ):
            raise ScreeningEligibilityError(
                "Eligiblility or `reasons ineligible` not set. "
                f"Got eligible={self.eligible}, reasons_ineligible={self.reasons_ineligible}. "
                "See method `assess_eligibility`."
            )
        if self.eligible == YES and self.reasons_ineligible:
            raise ScreeningEligibilityError(
                "Inconsistent result. Got eligible==YES where reasons_ineligible"
                f"is not None. Got reasons_ineligible={self.reasons_ineligible}"
            )
        if self.eligible == NO and not self.reasons_ineligible:
            raise ScreeningEligibilityError(
                "Inconsistent result. Got eligible==NO where reasons_ineligible is None"
            )
        self.update_model()

    def pre_assess_eligibility(self) -> None:
        return None

    @abstractmethod
    def assess_eligibility(self):
        """Asseses eligibility and finally sets the values of
        attrs `eligible` and `reasons ineligible`.
        """
        raise NotImplemented

    def update_model(self) -> None:
        """Updates the screening model.

        Since this class is instantiated in the model's save()
        method, no need to call save.
        """
        self.model_obj.eligible = self.is_eligible
        self.model_obj.reasons_ineligible = self.reasons_ineligible

    @property
    def is_eligible(self) -> bool:
        """Returns True if eligible else False"""
        return True if self.eligible == YES else False

    def format_reasons_ineligible(*values: str) -> str:
        reasons = None
        str_values = [x for x in values if x is not None]
        if str_values:
            str_values = "".join(str_values)
            reasons = format_html(str_values.replace("|", "<BR>"))
        return reasons

    @property
    def eligibility_display_label(self) -> str:
        if self.eligible == YES:
            return "ELIGIBLE"
        elif self.eligible == NO:
            return "INELIGIBLE"
        return TBD
