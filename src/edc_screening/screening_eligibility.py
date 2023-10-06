from __future__ import annotations

from typing import Any

from django.utils.html import format_html
from edc_constants.constants import NO, PENDING, TBD, YES

from .exceptions import (
    ScreeningEligibilityAttributeError,
    ScreeningEligibilityError,
    ScreeningEligibilityInvalidCombination,
    ScreeningEligibilityModelAttributeError,
)
from .fc import FC

__all__ = ["ScreeningEligibility"]


class ScreeningEligibility:
    """A class to calculate eligibility criteria."""

    eligible_display_label: str = "ELIGIBLE"
    eligible_fld_name: str = "eligible"
    eligible_value_default: str = TBD
    default_display_label = TBD
    eligible_values_list: list = [YES, NO, TBD]
    ineligible_display_label: str = "INELIGIBLE"
    is_eligible_value: str = YES
    is_ineligible_value: str = NO
    pending_value = PENDING
    pending_display_label = "PENDING"
    reasons_ineligible_fld_name: str = "reasons_ineligible"

    def __init__(
        self,
        model_obj: Any = None,
        cleaned_data: dict = None,
        eligible_value_default: str | None = None,
        eligible_values_list: list | None = None,
        is_eligible_value: str | None = None,
        is_ineligible_value: str | None = None,
        eligible_display_label: str | None = None,
        ineligible_display_label: str | None = None,
        update_model: bool | None = None,
    ) -> None:
        self.eligible: str = ""
        self.reasons_ineligible: dict[str, str] = {}
        self.model_obj = model_obj
        self.update_model: bool = True if update_model is None else update_model
        self.cleaned_data = cleaned_data
        if eligible_value_default:
            self.eligible_value_default = eligible_value_default
        if eligible_values_list:
            self.eligible_values_list = eligible_values_list
        if is_eligible_value:
            self.is_eligible_value = is_eligible_value
        if is_ineligible_value:
            self.is_ineligible_value = is_ineligible_value
        if eligible_display_label:
            self.eligible_display_label = eligible_display_label
        if ineligible_display_label:
            self.ineligible_display_label = ineligible_display_label

        self._assess_eligibility()

        if self.eligible not in self.eligible_values_list:
            raise ScreeningEligibilityError(
                f"Invalid value. See attr `eligible`. Expected one of "
                f"{self.eligible_values_list}. Got {self.eligible}."
            )
        if self.eligible == self.is_eligible_value and self.reasons_ineligible:
            raise ScreeningEligibilityInvalidCombination(
                "Inconsistent result. Got eligible==YES where reasons_ineligible"
                f"is not None. Got reasons_ineligible={self.reasons_ineligible}"
            )
        if self.eligible == self.is_ineligible_value and not self.reasons_ineligible:
            raise ScreeningEligibilityInvalidCombination(
                f"Inconsistent result. Got eligible=={self.eligible} "
                "where reasons_ineligible is None"
            )
        if self.model_obj and self.update_model:
            self._set_fld_attrs_on_model()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def assess_eligibility(self) -> None:
        """Override to add additional assessments after the default
        assessment is complete.

        Will only run if the default assessment returns `is eligible`
        """
        pass

    def get_required_fields(self) -> dict[str, FC | None]:
        """Returns a dict of {field_name: FC(value, msg), ...} needed
        to determine eligibility.

        * dict `key` is the field name. Should correspond with the model
          field name.
        * dict `value` is an `FC` instance.

        """
        return {}

    def set_fld_attrs_on_model(self) -> None:
        """Override to update additional model fields.

        Called after `assess_eligibity`.
        """
        pass

    @property
    def is_eligible(self) -> bool:
        """Returns True if eligible else False"""
        return True if self.eligible == self.is_eligible_value else False

    def _assess_eligibility(self) -> None:
        self.set_fld_attrs_on_self()
        self.eligible = self.is_eligible_value
        missing_data = self.get_missing_data()
        if missing_data:
            self.reasons_ineligible.update(**missing_data)
            self.eligible = self.eligible_value_default  # probably TBD
        for fldattr, fc in self.get_required_fields().items():
            if fldattr not in missing_data:
                if fc and fc.value:
                    msg = fc.msg if fc.msg else fldattr.title().replace("_", " ")
                    is_callable = False
                    try:
                        value = fc.value(getattr(self, fldattr))
                    except TypeError:
                        value = fc.value
                    else:
                        is_callable = True
                    if (
                        (isinstance(value, str) and getattr(self, fldattr) != value)
                        or (
                            isinstance(value, (list, tuple))
                            and getattr(self, fldattr) not in value
                        )
                        or (
                            isinstance(value, range)
                            and not (min(value) <= getattr(self, fldattr) <= max(value))
                        )
                        or (is_callable and value is False)
                    ):
                        self.reasons_ineligible.update({fldattr: msg})
                        self.eligible = self.is_ineligible_value  # probably NO
        if self.is_eligible:
            if self.is_eligible and not self.get_required_fields():
                self.eligible = self.eligible_value_default
            self.assess_eligibility()

    def _set_fld_attrs_on_model(self) -> None:
        """Updates screening model's eligibility field values.

        Called in the model.save() method so no need to call
        model.save().
        """
        setattr(
            self.model_obj,
            self.reasons_ineligible_fld_name,
            "|".join(self.reasons_ineligible.values()) or None,
        )
        self.set_eligible_model_field()
        self.set_fld_attrs_on_model()

    def set_eligible_model_field(self):
        setattr(self.model_obj, self.eligible_fld_name, self.is_eligible)

    def set_fld_attrs_on_self(self) -> None:
        """Adds fld attrs from the model / cleaned_data to self"""

        for fldattr in self.get_required_fields():
            try:
                getattr(self, fldattr)
            except AttributeError as e:
                raise ScreeningEligibilityAttributeError(
                    "Attribute refered to in `required_fields` does not exist on class. "
                    f"See {self.__class__.__name__}. "
                    f"Got {e}"
                )
            if self.model_obj:
                try:
                    value = (
                        self.cleaned_data.get(fldattr)
                        if self.cleaned_data
                        else getattr(self.model_obj, fldattr)
                    )
                except AttributeError as e:
                    raise ScreeningEligibilityModelAttributeError(
                        "Attribute does not exist on model. "
                        f"See {self.model_obj.__class__.__name__}. "
                        f"Got {e}"
                    )
            else:
                value = self.cleaned_data.get(fldattr)
            setattr(self, fldattr, value)

    def get_missing_data(self) -> dict:
        missing_responses = {}
        for fldattr, fc in self.get_required_fields().items():
            if fc and not fc.ignore_if_missing:
                value = getattr(self, fldattr)
                if value:
                    if fc.missing_value and value == fc.missing_value:
                        missing_responses.update({fldattr: None})
                else:
                    missing_responses.update({fldattr: value})
        return {
            k: f"`{k.replace('_', ' ').title()}` not answered"
            for k, v in missing_responses.items()
            if not v
        }

    def formatted_reasons_ineligible(self) -> str:
        str_values = "<BR>".join(
            [x for x in self.reasons_ineligible.values() if x is not None]
        )
        return format_html(str_values)

    @property
    def display_label(self) -> str:
        display_label = self.eligible
        if self.eligible == self.is_eligible_value:
            display_label = self.eligible_display_label
        elif self.eligible == self.is_ineligible_value:
            display_label = self.ineligible_display_label
        elif self.eligible == self.eligible_value_default:
            display_label = self.default_display_label
        elif self.eligible == self.pending_value:
            display_label = self.pending_display_label
        return display_label
