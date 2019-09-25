from copy import copy
from django.apps import apps as django_apps
from edc_constants.constants import YES

from .reportables_evaluator import ReportablesEvaluator


class ReportablesFormValidatorMixin:

    reportables_cls = ReportablesEvaluator

    def validate_reportable_fields(self, reference_list_name, **extra_options):
        """Called in clean() method of the FormValidator.

        for example:

            def clean(self):
                ...
                self.validate_reportable_fields(reference_list_name="ambition")
                ...
        """

        subject_visit = self.cleaned_data.get("subject_visit")
        RegisteredSubject = django_apps.get_model("edc_registration.registeredsubject")
        subject_identifier = self.cleaned_data.get("subject_visit").subject_identifier
        registered_subject = RegisteredSubject.objects.get(
            subject_identifier=subject_identifier
        )

        # check normal ranges and grade result values
        reportables = self.reportables_cls(
            reference_list_name=reference_list_name,
            cleaned_data=copy(self.cleaned_data),
            gender=registered_subject.gender,
            dob=registered_subject.dob,
            report_datetime=subject_visit.report_datetime,
            **extra_options,
        )
        reportables.validate_reportable_fields()

        reportables.validate_results_abnormal_field()
        self.applicable_if(
            YES, field="results_abnormal", field_applicable="results_reportable"
        )
        reportables.validate_results_reportable_field(responses=self.reportable_grades)
