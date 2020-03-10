from django.db import models
from edc_action_item.models import ActionModelMixin
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_identifier.model_mixins import TrackingModelMixin
from edc_registration.models import RegisteredSubject
from edc_reportable import site_reportables
from edc_visit_tracking.managers import CrfModelManager, CurrentSiteManager


class BloodResultsModelMixin(ActionModelMixin, TrackingModelMixin, models.Model):

    action_name = None

    results_abnormal = models.CharField(
        verbose_name="Are any of the above results abnormal?",
        choices=YES_NO,
        max_length=25,
    )

    results_reportable = models.CharField(
        verbose_name="If any results are abnormal, are results within grade 3 "
        "or above?",
        max_length=25,
        choices=YES_NO_NA,
        help_text="If YES, this value will open Adverse Event Form.",
    )

    summary = models.TextField(null=True, blank=True)

    on_site = CurrentSiteManager()

    objects = CrfModelManager()

    def save(self, *args, **kwargs):
        self.summary = "\n".join(self.get_summary())
        super().save(*args, **kwargs)

    def get_summary_options(self):
        registered_subject = RegisteredSubject.objects.get(
            subject_identifier=self.subject_visit.subject_identifier
        )
        return dict(
            gender=registered_subject.gender,
            dob=registered_subject.dob,
            report_datetime=self.subject_visit.report_datetime,
        )

    def get_summary(self):
        opts = self.get_summary_options()
        summary = []
        for field in [f.name for f in self._meta.fields]:
            grp = site_reportables.get("meta").get(field)
            value = getattr(self, field)
            if value and grp:
                units = getattr(self, f"{field}_units")
                opts.update(units=units)
                grade = grp.get_grade(value, **opts)
                if grade and grade.grade:
                    summary.append(f"{field}: {grade.description}.")
                elif not grade:
                    normal = grp.get_normal(value, **opts)
                    if not normal:
                        summary.append(f"{field}: {value} {units} is abnormal")
        return summary

    def get_action_item_reason(self):
        return self.summary

    @property
    def abnormal(self):
        return self.results_abnormal

    @property
    def reportable(self):
        return self.results_reportable

    class Meta:
        abstract = True
