from typing import Optional, Union

from django.db import models
from django.utils.html import format_html
from edc_constants.constants import NO, TBD, YES


class FC:
    """A simple class of the eligible criteria for a field.

    value: value if eligible
    msg: message if value is NOT met / ineligible
    ignore_if_missing: skip assessment if the field does not have a value
    """

    def __init__(
        self,
        value: Optional[Union[str, list, tuple, range]] = None,
        msg: Optional[str] = None,
        ignore_if_missing: Optional[bool] = False,
        missing_value: Optional[str] = None,
    ):
        self.value = value
        self.msg = msg
        self.ignore_if_missing = ignore_if_missing
        self.missing_value = missing_value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value, self.msg, self.ignore_if_missing})"


class ScreeningEligibilityError(Exception):
    pass


class ScreeningEligibilityAttributeError(Exception):
    pass


class ScreeningEligibilityModelAttributeError(Exception):
    pass


class ScreeningEligibilityCleanedDataKeyError(Exception):
    pass


class ScreeningEligibilityInvalidCombination(Exception):
    pass


class RequiredFieldValueMissing(Exception):
    pass


class ScreeningEligibility:
    """A class to calculate eligibility criteria."""

    eligible_display_label: str = "ELIGIBLE"
    eligible_fld_name: str = "eligible"
    eligible_value_default: str = TBD
    eligible_values_list: list = [YES, NO, TBD]
    ineligible_display_label: str = "INELIGIBLE"
    is_eligible_value: str = YES
    is_ineligible_value: str = NO
    reasons_ineligible_fld_name: str = "reasons_ineligible"

    def __init__(
        self,
        model_obj: Optional[models.Model] = None,
        cleaned_data: Optional[dict] = None,
        eligible_value_default: Optional[str] = None,
        eligible_values_list: Optional[list] = None,
        is_eligible_value: Optional[str] = None,
        is_ineligible_value: Optional[str] = None,
        eligible_display_label: Optional[str] = None,
        ineligible_display_label: Optional[str] = None,
        verbose: Optional[bool] = None,
        update_model: Optional[bool] = None,
    ) -> None:

        self.verbose = verbose
        self.update_model = True if update_model is None else update_model
        self.cleaned_data = cleaned_data
        self.eligible = self.eligible_value_default
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
        self.model_obj = model_obj
        self.reasons_ineligible = {}
        self._assess_eligibility()
        if self.eligible not in self.eligible_values_list:
            raise ScreeningEligibilityError(
                f"Invalid value. See attr `eligible`. Expected one of "
                f"{self.eligible_values_list}. Got {self.eligible}."
            )
        if (
            not self.eligible
            or self.eligible not in self.eligible_values_list
            or self.reasons_ineligible is None
        ):
            raise ScreeningEligibilityError(
                "Eligiblility or `reasons ineligible` not set. "
                f"Got eligible={self.eligible}, reasons_ineligible={self.reasons_ineligible}. "
                "See method `assess_eligibility`."
            )
        if self.eligible == self.is_eligible_value and self.reasons_ineligible:
            raise ScreeningEligibilityInvalidCombination(
                "Inconsistent result. Got eligible==YES where reasons_ineligible"
                f"is not None. Got reasons_ineligible={self.reasons_ineligible}"
            )
        if self.eligible != self.is_eligible_value and not self.reasons_ineligible:
            raise ScreeningEligibilityInvalidCombination(
                f"Inconsistent result. Got eligible=={self.eligible} "
                "where reasons_ineligible is None"
            )
        if self.model_obj and self.update_model:
            self._set_fld_attrs_on_model()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def assess_eligibility(self) -> None:
        """Override to add additional assessments after the default
        assessment is complete.

        Will only run if the default assessment returns is eligible
        """
        pass

    def get_required_fields(self) -> dict[str, FC]:
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
                    if self.verbose:
                        msg = f"{msg}. Got {fldattr}={getattr(self, fldattr)}"
                    if (
                        (type(fc.value) == str and getattr(self, fldattr) != fc.value)
                        or (
                            type(fc.value) in (list, tuple)
                            and getattr(self, fldattr) not in fc.value
                        )
                        or (
                            type(fc.value) in (range,)
                            and not (min(fc.value) <= getattr(self, fldattr) <= max(fc.value))
                        )
                    ):
                        self.reasons_ineligible.update({fldattr: msg})
                        self.eligible = self.is_ineligible_value  # probably NO
        if self.is_eligible:
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
        setattr(self.model_obj, self.eligible_fld_name, self.eligible)
        self.set_fld_attrs_on_model()

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
                try:
                    value = self.cleaned_data[fldattr]
                except KeyError as e:
                    raise ScreeningEligibilityCleanedDataKeyError(
                        "Attribute does not exist in cleaned_data. " f"Got {e}"
                    )
            setattr(self, fldattr, value)

    def get_missing_data(self) -> dict:
        missing_responses = {}
        for fldattr, fc in self.get_required_fields().items():
            if not fc.ignore_if_missing:
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
        return display_label
