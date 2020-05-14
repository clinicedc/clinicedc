from django.core.exceptions import ObjectDoesNotExist
from edc_visit_schedule import site_visit_schedules
from import_export.fields import Field
from import_export.resources import ModelResource

from .models import Appointment


class AppointmentResource(ModelResource):

    offstudy_datetime = Field(column_name="offstudy_datetime")

    def dehydrate_offstudy(self, obj):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=obj.visit_schedule_name
        )
        schedule = visit_schedule.schedules.get(obj.schedule_name)
        try:
            off_schedule_obj = schedule.offschedule_model_cls.objects.get(
                subject_identifier=obj.subject_identifier,
                report_datetime__lte=obj.appt_datetime,
            )
        except ObjectDoesNotExist:
            return None
        return off_schedule_obj.offschedule_datetime

    class Meta:
        model = Appointment
