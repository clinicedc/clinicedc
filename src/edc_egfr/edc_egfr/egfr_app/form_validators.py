from copy import copy

from dateutil.relativedelta import relativedelta
from edc_constants.constants import MALE, YES
from edc_form_validators import FormValidator
from edc_reportable.forms import ReportablesFormValidatorMixin
from edc_utils.date import get_utcnow


class SpecimenResultFormValidator(ReportablesFormValidatorMixin, FormValidator):
    reference_range_collection_name = "my_reference_list"

    def clean(self):
        self.validate_reportable_fields()

    def validate_reportable_fields(self, *args, **kwargs):
        reference_range_evaluator = self.reference_range_evaluator_cls(
            self.reference_range_collection_name,
            cleaned_data=copy(self.cleaned_data),
            gender=MALE,
            dob=get_utcnow() - relativedelta(years=25),
            report_datetime=get_utcnow(),
        )
        reference_range_evaluator.validate_reportable_fields()

        reference_range_evaluator.validate_results_abnormal_field()

        self.applicable_if(
            YES, field="results_abnormal", field_applicable="results_reportable"
        )

        reference_range_evaluator.validate_results_reportable_field()
