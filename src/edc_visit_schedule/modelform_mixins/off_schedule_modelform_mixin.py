from django.forms import ValidationError

from ..site_visit_schedules import site_visit_schedules
from ..subject_schedule import InvalidOffscheduleDate


class OffScheduleModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        subject_identifier = cleaned_data.get("subject_identifier")
        offschedule_datetime = cleaned_data.get("offschedule_datetime")
        visit_schedule, schedule = site_visit_schedules.get_by_offschedule_model(
            self._meta.model._meta.label_lower
        )
        history_obj = schedule.history_model_cls.objects.get(
            subject_identifier=subject_identifier,
            schedule_name=schedule.name,
            visit_schedule_name=visit_schedule.name,
        )
        try:
            schedule.subject.update_history_or_raise(
                history_obj=history_obj,
                subject_identifier=subject_identifier,
                offschedule_datetime=offschedule_datetime,
                update=False,
            )
        except InvalidOffscheduleDate as e:
            raise ValidationError(e)
        return cleaned_data
