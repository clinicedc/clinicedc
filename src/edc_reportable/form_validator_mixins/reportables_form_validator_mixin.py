from copy import deepcopy

from edc_constants.constants import YES
from edc_registration import get_registered_subject_model_cls

from ..reportables_evaluator import ReportablesEvaluator


class ReportablesFormValidatorMixin:
    reportables_cls = ReportablesEvaluator
    value_field_suffix = "_value"

    @property
    def reportables_evaluator_options(self):
        return {}

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
        # cleaned_data.update(subject_visit=self.related_visit)
        registered_subject = get_registered_subject_model_cls().objects.get(
            subject_identifier=self.subject_identifier
        )
        # check normal ranges and grade result values
        reportables = self.reportables_cls(
            reference_range_collection_name,
            cleaned_data=deepcopy(cleaned_data),
            gender=registered_subject.gender,
            dob=registered_subject.dob,
            report_datetime=self.report_datetime,
            value_field_suffix=self.value_field_suffix,
            **reportables_evaluator_options,
        )
        reportables.validate_reportable_fields()

        reportables.validate_results_abnormal_field()
        self.applicable_if(
            YES, field="results_abnormal", field_applicable="results_reportable"
        )
        reportables.validate_results_reportable_field()
