from copy import deepcopy

from edc_constants.constants import YES
from edc_form_validators import INVALID_ERROR
from edc_registration import get_registered_subject_model_cls

__all__ = ["ReportablesFormValidatorMixin"]

from ..exceptions import NotEvaluated
from ..reference_range_evaluator import ReferenceRangeEvaluator


class ReportablesFormValidatorMixin:
    value_field_suffix = "_value"
    reference_range_evaluator_cls = ReferenceRangeEvaluator

    @property
    def age_units(self):
        return "years"

    @property
    def reportables_evaluator_options(self):
        return {"age_units": "years"}

    def validate_reportable_fields(
        self, reference_range_collection_name: str, **reportables_evaluator_options
    ):
        """Called in clean() method of the FormValidator.

        for example:

            def clean(self):
                ...
                self.validate_reportable_fields()
                ...
        """

        cleaned_data = deepcopy(self.cleaned_data)
        registered_subject = get_registered_subject_model_cls().objects.get(
            subject_identifier=self.subject_identifier
        )
        # check normal ranges and grade result values
        options = dict(
            cleaned_data=deepcopy(cleaned_data),
            gender=registered_subject.gender,
            dob=registered_subject.dob,
            report_datetime=self.report_datetime,
            value_field_suffix=self.value_field_suffix,
        )
        options.update(**reportables_evaluator_options)
        reference_range_evaluator = self.reference_range_evaluator_cls(
            reference_range_collection_name, **options
        )
        try:
            reference_range_evaluator.validate_reportable_fields()
        except NotEvaluated as e:
            self.raise_validation_error({"__all__": str(e)}, INVALID_ERROR)
        reference_range_evaluator.validate_results_abnormal_field()
        self.applicable_if(
            YES, field="results_abnormal", field_applicable="results_reportable"
        )
        reference_range_evaluator.validate_results_reportable_field()
