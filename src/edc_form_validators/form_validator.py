from .applicable_field_validator import ApplicableFieldValidator
from .base_form_validator import BaseFormValidator
from .date_range_validator import DateRangeFieldValidator
from .date_validator import DateValidator
from .many_to_many_field_validator import ManyToManyFieldValidator
from .other_specify_field_validator import OtherSpecifyFieldValidator
from .range_field_validator import RangeFieldValidator
from .required_field_validator import RequiredFieldValidator


class FormValidator(
    RequiredFieldValidator,
    ManyToManyFieldValidator,
    OtherSpecifyFieldValidator,
    ApplicableFieldValidator,
    RangeFieldValidator,
    DateRangeFieldValidator,
    DateValidator,
    BaseFormValidator,
):
    pass
