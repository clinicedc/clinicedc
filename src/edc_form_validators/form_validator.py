from .applicable_field_validator import ApplicableFieldValidator
from .base_form_validator import BaseFormValidator
from .many_to_many_field_validator import ManyToManyFieldValidator
from .other_specify_field_validator import OtherSpecifyFieldValidator
from .required_field_validator import RequiredFieldValidator


class FormValidator(
    RequiredFieldValidator,
    ManyToManyFieldValidator,
    OtherSpecifyFieldValidator,
    ApplicableFieldValidator,
    BaseFormValidator,
):

    pass
