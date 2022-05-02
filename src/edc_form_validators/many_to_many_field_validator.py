from typing import Optional, Union

from django.forms import ValidationError
from edc_constants.constants import NOT_APPLICABLE, OTHER

from .base_form_validator import (
    APPLICABLE_ERROR,
    NOT_APPLICABLE_ERROR,
    NOT_REQUIRED_ERROR,
    REQUIRED_ERROR,
    BaseFormValidator,
)

M2M_SELECTION_ONLY = "m2m_selection_only"
M2M_INVALID_SELECTION = "m2m_invalid_selection"
M2M_INVALID_COMBINATION = "m2m_invalid_combination"


class ManyToManyFieldValidator(BaseFormValidator):
    def get_m2m_selected(self, m2m_field: str) -> dict:
        qs = self.cleaned_data.get(m2m_field) or []
        return {
            getattr(obj, self.default_fk_stored_field_name): getattr(
                obj, self.default_fk_display_field_name
            )
            for obj in qs
        }

    def m2m_applicable_if_true(self, cond: bool, m2m_field: str = None) -> bool:
        code: Optional[str] = None
        message: dict = {}
        qs = self.cleaned_data.get(m2m_field)
        if cond:
            if qs and qs.count() > 0:
                selected = self.get_m2m_selected(m2m_field)
                if NOT_APPLICABLE in selected:
                    message = {m2m_field: "This field is applicable"}
                    code = APPLICABLE_ERROR
        else:
            if qs and qs.count() > 0:
                selected = self.get_m2m_selected(m2m_field)
                if NOT_APPLICABLE not in selected:
                    message = {m2m_field: "This field is not applicable"}
                    code = NOT_APPLICABLE_ERROR
        if message:
            self._errors.update(message)
            self._error_codes.append(code)
            raise ValidationError(message, code=code)
        return False

    def m2m_applicable_if(
        self, *responses: Union[str, int, bool], field: str = None, m2m_field: str = None
    ) -> bool:
        """Raises an exception or returns False.

        m2m_field is applicable if field is in responses.
        """
        code: Optional[str] = None
        message: dict = {}
        if self.cleaned_data.get(field):
            qs = self.cleaned_data.get(m2m_field)
            if self.cleaned_data.get(field) not in responses:
                # m2m should == NOT_APPLICABLE
                if qs and qs.count() > 0:
                    selected = self.get_m2m_selected(m2m_field)
                    if NOT_APPLICABLE not in selected:
                        message = {m2m_field: "This field is not applicable"}
                        code = NOT_APPLICABLE_ERROR
            else:
                # m2m should != NOT_APPLICABLE
                if qs and qs.count() > 0:
                    selected = self.get_m2m_selected(m2m_field)
                    if NOT_APPLICABLE in selected:
                        message = {m2m_field: "This field is applicable"}
                        code = APPLICABLE_ERROR
        if message:
            self._errors.update(message)
            self._error_codes.append(code)
            raise ValidationError(message, code=code)
        return False

    def m2m_required(self, m2m_field: str = None) -> bool:
        """Raises an exception or returns False.

        m2m_field is required.
        """
        code: Optional[str] = None
        message: dict = {}
        if not self.cleaned_data.get(m2m_field):
            message = {m2m_field: "This field is required"}
            code = REQUIRED_ERROR
        if message:
            self._errors.update(message)
            self._error_codes.append(code)
            raise ValidationError(message, code=code)
        return False

    def m2m_not_required(self, m2m_field: str = None) -> bool:
        """Raises an exception or returns False.

        m2m_field is not required.
        """
        code: Optional[str] = None
        message: dict = {}
        if self.cleaned_data.get(m2m_field):
            message = {m2m_field: "This field is not required"}
            code = REQUIRED_ERROR
        if message:
            self._errors.update(message)
            self._error_codes.append(code)
            raise ValidationError(message, code=code)
        return False

    def m2m_required_if(
        self, response: Union[str, int, bool], field: str = None, m2m_field: str = None
    ) -> bool:
        """Raises an exception or returns False.

        m2m_field is required if field  == response
        """
        code: Optional[str] = None
        message: dict = {}
        if self.cleaned_data.get(field) == response and not self.cleaned_data.get(m2m_field):
            message = {m2m_field: "This field is required"}
            code = REQUIRED_ERROR
        elif (
            self.cleaned_data.get(field) == response
            and self.cleaned_data.get(m2m_field).count() == 0
        ):
            message = {m2m_field: "This field is required"}
            code = REQUIRED_ERROR
        elif (
            self.cleaned_data.get(field) != response
            and self.cleaned_data.get(m2m_field)
            and self.cleaned_data.get(m2m_field).count() != 0
        ):
            message = {m2m_field: "This field is not required"}
            code = NOT_REQUIRED_ERROR
        if message:
            self._errors.update(message)
            self._error_codes.append(code)
            raise ValidationError(message, code=code)
        return False

    def m2m_single_selection_if(self, *single_selections: str, m2m_field=None):
        """Raises an exception of returns False.

        if a selected response from m2m_field is in single_selections
        and there is more than one selected value, raises.
        """
        qs = self.cleaned_data.get(m2m_field)
        if qs and qs.count() > 1:
            selected = self.get_m2m_selected(m2m_field)
            for selection in single_selections:
                if selection in selected:
                    message = {
                        m2m_field: f"Invalid combination. '{selected.get(selection)}' "
                        f"may not be combined "
                        f"with other selections"
                    }
                    self._errors.update(message)
                    self._error_codes.append(M2M_INVALID_COMBINATION)
                    raise ValidationError(message, code=M2M_INVALID_COMBINATION)
        return False

    def m2m_other_specify(
        self,
        *responses: Union[str, int, bool],
        m2m_field: str = None,
        field_other: Optional[str] = None,
        field_other_evaluate_as_int: Optional[bool] = None,
    ) -> bool:
        """Raises an exception or returns False.

        field_other is required if a selected response from m2m_field
        is in responses

        Note: for edc list models, "name" is the stored value!
        """
        qs = self.cleaned_data.get(m2m_field)
        found = False
        responses = (OTHER,) if len(responses) == 0 else responses

        if field_other_evaluate_as_int:
            field_other_has_value = self.cleaned_data.get(field_other) is not None
        else:
            field_other_has_value = self.cleaned_data.get(field_other)
        if qs and qs.count() > 0:
            for response in responses:
                if response in self.get_m2m_selected(m2m_field):
                    found = True
            if found and not field_other_has_value:
                message = {field_other: "This field is required."}
                self._errors.update(message)
                self._error_codes.append(REQUIRED_ERROR)
                raise ValidationError(message, code=REQUIRED_ERROR)
            elif not found and field_other_has_value:
                message = {field_other: "This field is not required."}
                self._errors.update(message)
                self._error_codes.append(NOT_REQUIRED_ERROR)
                raise ValidationError(message, code=NOT_REQUIRED_ERROR)
        elif field_other_has_value:
            message = {field_other: "This field is not required."}
            self._errors.update(message)
            self._error_codes.append(NOT_REQUIRED_ERROR)
            raise ValidationError(message, code=NOT_REQUIRED_ERROR)
        return False

    def m2m_other_not_specify(
        self,
        *responses: Union[str, int, bool],
        m2m_field: str = None,
        field_other: Optional[str] = None,
    ) -> bool:
        """Raises an exception or returns False.

        field_other is NOT required if a selected response from m2m_field
        is in responses

        Note: for edc list models, "name" is the stored value!
        """
        qs = self.cleaned_data.get(m2m_field)
        found = False
        if qs and qs.count() > 0:
            for response in responses:
                if response in self.get_m2m_selected(m2m_field):
                    found = True
            if found and self.cleaned_data.get(field_other):
                message = {field_other: "This field is not required."}
                self._errors.update(message)
                self._error_codes.append(NOT_REQUIRED_ERROR)
                raise ValidationError(message, code=NOT_REQUIRED_ERROR)
            elif not found and not self.cleaned_data.get(field_other):
                message = {field_other: "This field is required."}
                self._errors.update(message)
                self._error_codes.append(REQUIRED_ERROR)
                raise ValidationError(message, code=REQUIRED_ERROR)
        elif self.cleaned_data.get(field_other):
            message = {field_other: "This field is not required."}
            self._errors.update(message)
            self._error_codes.append(NOT_REQUIRED_ERROR)
            raise ValidationError(message, code=NOT_REQUIRED_ERROR)
        return False

    def m2m_other_specify_applicable(
        self,
        *responses: Union[str, int, bool],
        m2m_field: str = None,
        field_other: Optional[str] = None,
    ) -> bool:
        """Raises an exception or returns False.

        field_other is applicable if a selected response from m2m_field
        is in responses
        """
        selected = self.cleaned_data.get(m2m_field)
        found = False
        if selected and selected.count() > 0:
            for response in responses:
                if response in [
                    getattr(o, self.default_fk_stored_field_name) for o in selected
                ]:
                    found = True
            if found and self.cleaned_data.get(field_other) == NOT_APPLICABLE:
                message = {field_other: "This field is applicable."}
                self._errors.update(message)
                self._error_codes.append(APPLICABLE_ERROR)
                raise ValidationError(message, code=APPLICABLE_ERROR)
            elif not found and self.cleaned_data.get(field_other) != NOT_APPLICABLE:
                message = {field_other: "This field is not applicable."}
                self._errors.update(message)
                self._error_codes.append(NOT_APPLICABLE_ERROR)
                raise ValidationError(message, code=NOT_APPLICABLE_ERROR)
        elif self.cleaned_data.get(field_other) != NOT_APPLICABLE:
            message = {field_other: "This field is not applicable."}
            self._errors.update(message)
            self._error_codes.append(NOT_APPLICABLE_ERROR)
            raise ValidationError(message, code=NOT_APPLICABLE_ERROR)
        return False

    def m2m_selection_expected(
        self, response: Union[str, int, bool], m2m_field: str = None, error_msg: str = None
    ) -> bool:
        """Raises an exception or returns False.

        m2m_field is required and the selection must be `response`
        and only `response`.

        This would normally be preceded by an IF condition in the code.

            if (condition):
                self.m2m_selection_expected(...)
        """
        qs = self.cleaned_data.get(m2m_field)
        if qs and qs.count() > 0:
            selection = [
                getattr(obj, self.default_fk_stored_field_name)
                for obj in qs
                if getattr(obj, self.default_fk_stored_field_name) == response
            ]
            if not selection or qs.count() > 1:
                message = {m2m_field: error_msg or f"Expected {response} only."}
                self._errors.update(message)
                self._error_codes.append(M2M_SELECTION_ONLY)
                raise ValidationError(message, code=M2M_SELECTION_ONLY)
        return False

    def m2m_selections_not_expected(
        self,
        *responses: Union[str, int, bool],
        m2m_field: str = None,
        error_msg: Optional[str] = None,
    ) -> bool:
        """Raises an exception or returns False.

        m2m_field is required but no selections may be in `responses`.
        """
        qs = self.cleaned_data.get(m2m_field)
        if qs and qs.count() > 0:
            selections = [
                getattr(obj, self.default_fk_stored_field_name)
                for obj in qs
                if getattr(obj, self.default_fk_stored_field_name) in responses
            ]
            if selections:
                display_names = ", ".join(
                    [
                        getattr(obj, self.default_fk_display_field_name)
                        for obj in qs
                        if getattr(obj, self.default_fk_stored_field_name) in responses
                    ]
                )
                message = {
                    m2m_field: error_msg
                    or f"Invalid selection. " f"Cannot be any of: {display_names}."
                }
                self._errors.update(message)
                self._error_codes.append(M2M_INVALID_SELECTION)
                raise ValidationError(message, code=M2M_INVALID_SELECTION)
        return False
