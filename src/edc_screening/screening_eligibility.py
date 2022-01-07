import pdb
from abc import ABC, abstractmethod
from typing import Optional

from django.db import models
from django.utils.html import format_html
from edc_constants.constants import NO, TBD, YES


class ScreeningEligibilityError(Exception):
    pass


class ScreeningEligibility(ABC):
    def __init__(self, model_obj: models.Model = None, allow_none: Optional[bool] = None):
        self.model_obj = model_obj
        self.eligible: str = NO  # YES, NO or TBD
        self.reasons_ineligible: dict = {}
        self.allow_none = allow_none  # TODO: allow_none ??
        self.pre_assess_eligibility()
        self.assess_eligibility()
        if self.eligible == YES and self.reasons_ineligible:
            raise ScreeningEligibilityError(
                "Inconsistent result. Got eligible where reasons_ineligible is not none"
            )
        self.update_model()

    def pre_assess_eligibility(self) -> None:
        return None

    @abstractmethod
    def assess_eligibility(self):
        raise NotImplemented

    @abstractmethod
    def update_model(self) -> None:
        raise NotImplemented

    @property
    def is_eligible(self) -> bool:
        """Returns True if eligible else False"""
        return True if self.eligible == YES else False

    # @property
    # @abstractmethod
    # def eligible(self) -> str:
    #     """Returns YES, NO or TBD."""
    #     return TBD

    # @property
    # @abstractmethod
    # def reasons_ineligible(self) -> dict:
    #     """Returns a dictionary of reasons ineligible or None."""
    #     return {}

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
