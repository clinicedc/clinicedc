from typing import Any

from django.apps import apps as django_apps
from django.db import models
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_reportable.site_reportables import site_reportables


class BloodResultsFieldsModelMixin(models.Model):

    results_abnormal = models.CharField(
        verbose_name="Are any of the above results abnormal?",
        choices=YES_NO,
        max_length=25,
    )

    results_reportable = models.CharField(
        verbose_name="If any results are abnormal, are results within grade 3 " "or above?",
        max_length=25,
        choices=YES_NO_NA,
        help_text="If YES, this value will open Adverse Event Form.",
    )

    summary = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class BloodResultsMethodsModelMixin(models.Model):

    """Requires additional attrs `subject_visit` and `requisition`"""

    def save(self, *args, **kwargs):
        self.summary = "\n".join(self.get_summary())
        super().save(*args, **kwargs)

    def get_summary_options(self: Any) -> dict:
        model_cls = django_apps.get_model("edc_registration.registeredsubject")
        registered_subject = model_cls.objects.get(
            subject_identifier=self.subject_visit.subject_identifier
        )
        return dict(
            gender=registered_subject.gender,
            dob=registered_subject.dob,
            report_datetime=self.subject_visit.report_datetime,
        )

    def get_reference_range_collection_name(self: Any) -> str:
        return self.requisition.panel_object.reference_range_collection_name

    def get_summary(self: Any) -> list:
        opts = self.get_summary_options()
        summary = []
        for field_name in [f.name for f in self._meta.fields]:
            try:
                utest_id, _ = field_name.split("_value")
            except ValueError:
                utest_id = field_name
            if reference_grp := site_reportables.get(
                self.get_reference_range_collection_name()
            ).get(utest_id):
                if value := getattr(self, field_name):
                    units = getattr(self, f"{utest_id}_units")
                    opts.update(units=units)
                    grade = reference_grp.get_grade(value, **opts)
                    if grade and grade.grade:
                        setattr(self, f"{utest_id}_grade", grade.grade)
                        setattr(self, f"{utest_id}_grade_description", grade.description)
                        summary.append(f"{field_name}: {grade.description}.")
                    elif not grade:
                        normal = reference_grp.get_normal(value, **opts)
                        if not normal:
                            summary.append(f"{field_name}: {value} {units} is abnormal")
        return summary

    def get_action_item_reason(self):
        return self.summary

    @property
    def abnormal(self: Any):
        return self.results_abnormal

    @property
    def reportable(self: Any):
        return self.results_reportable

    class Meta:
        abstract = True


class BloodResultsModelMixin(
    BloodResultsFieldsModelMixin, BloodResultsMethodsModelMixin, models.Model
):
    """For each `result` the field name or its prefix should
    match with a value in reportables.

    For example:
        field_name = creatinine_value
        reportables name: creatinine
        value_field_suffix = "_value"

        -OR-

        field_name = creatinine
        reportables name: creatinine
        value_field_suffix = None

    Requires additional attrs `subject_visit` and `requisition`
    from CrfWithRequisitionModelMixin

    """

    class Meta:
        abstract = True
