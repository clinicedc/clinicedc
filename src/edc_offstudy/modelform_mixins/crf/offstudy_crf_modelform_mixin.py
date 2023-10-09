from django import forms
from django.core.exceptions import ObjectDoesNotExist
from edc_utils import formatted_datetime
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...utils import OffstudyError, raise_if_offstudy


class OffstudyCrfModelFormMixin:

    """ModelForm mixin for CRF Models.

    Must be declared with at least VisitScheduleCrfModelFormMixin
    """

    def clean(self):
        cleaned_data = super().clean()
        self.raise_if_offstudy_by_report_datetime()
        self.raise_if_offschedule_by_report_datetime()
        return cleaned_data

    def raise_if_offschedule_by_report_datetime(self):
        """Raises a ValidationError if the subject is offschedule before
        the report_datetime.
        """
        if self.subject_identifier and self.report_datetime:
            visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
            schedule = visit_schedule.schedules.get(self.schedule_name)
            try:
                offschedule_obj = schedule.offschedule_model_cls.objects.get(
                    subject_identifier=self.subject_identifier,
                    offschedule_datetime__lt=self.report_datetime,
                )
            except ObjectDoesNotExist:
                pass
            else:
                offschedule_datetime = formatted_datetime(offschedule_obj.offschedule_datetime)
                raise forms.ValidationError(
                    f"Subject was taken off schedule before this report datetime. "
                    f"Got subject_identifier='{self.subject_identifier}', "
                    f"schedule='{visit_schedule.name}.{schedule.name}, '"
                    f"offschedule date='{offschedule_datetime}'."
                )

    def raise_if_offstudy_by_report_datetime(self):
        """Raises a ValidationError on a CRF if the subject is
        off study before the report_datetime.
        """
        if self.report_datetime:
            try:
                raise_if_offstudy(
                    source_obj=self.instance,
                    subject_identifier=self.subject_identifier,
                    report_datetime=self.report_datetime,
                )
            except OffstudyError as e:
                raise forms.ValidationError(e)
