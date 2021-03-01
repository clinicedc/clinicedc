from abc import ABC, abstractmethod
from typing import Optional

from django.db import models
from django.utils.html import format_html


class ScreeningEligibility(ABC):
    def __init__(self, model_obj: models.Model = None, allow_none: Optional[bool] = None):
        self.model_obj = model_obj
        self.allow_none = allow_none

    @property
    @abstractmethod
    def eligible(self) -> bool:
        """Returns True or False."""
        return False

    @property
    @abstractmethod
    def reasons_ineligible(self) -> Optional[dict]:
        """Returns a dictionary of reasons ineligible or None."""
        return None

    def format_reasons_ineligible(*values: str) -> str:
        reasons = None
        str_values = [x for x in values if x is not None]
        if str_values:
            str_values = "".join(str_values)
            reasons = format_html(str_values.replace("|", "<BR>"))
        return reasons

    def eligibility_display_label(self) -> str:
        return "ELIGIBLE" if self.eligible else "not eligible"
