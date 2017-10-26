import arrow

from dateutil.relativedelta import relativedelta, SA, SU

from django.apps import apps as django_apps
from django.db import models
from django.db.models import options
from django.db.models.deletion import ProtectedError

from ..appointment_creator import AppointmentCreator


if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class CreateAppointmentsMixin(models.Model):
    """ Model Mixin to add fields and methods to an enrollment
    model to create appointments on post_save.

    Requires model mixins VisitScheduleFieldsModelMixin,
    VisitScheduleMethodsModelMixin.
    """

    appointment_creator_cls = AppointmentCreator

    facility_name = models.CharField(
        verbose_name='To which facility is this subject being enrolled?',
        max_length=25,
        default='clinic',
        help_text='The facility name is need when scheduling appointments')

    def create_appointments(self, base_appt_datetime=None, taken_datetimes=None):
        """Creates appointments when called by post_save signal.

        Timepoint datetimes are adjusted according to the available
        days in the facility.
        """
        app_config = django_apps.get_app_config('edc_facility')
        appointments = []
        taken_datetimes = taken_datetimes or []
        base_appt_datetime = base_appt_datetime or self.report_datetime
        base_appt_datetime = arrow.Arrow.fromdatetime(
            base_appt_datetime, base_appt_datetime.tzinfo).to('utc').datetime
        facility = app_config.get_facility(self.facility_name)
        timepoint_dates = self.schedule.visits.timepoint_dates(
            dt=base_appt_datetime)
        for visit, timepoint_datetime in timepoint_dates.items():
            available_rdate = facility.available_rdate(
                suggested_datetime=timepoint_datetime,
                reverse_delta=visit.rlower,
                forward_delta=visit.rupper,
                taken_datetimes=taken_datetimes)
            appointment = self.update_or_create_appointment(
                visit, available_rdate.datetime, timepoint_datetime)
            appointments.append(appointment)
            taken_datetimes.append(available_rdate.datetime)
        return appointments

#     def move_to_facility_day(self, facility, dt, forward_only=None):
#         """Move a date forward off of a weekend unless app_config
#         includes weekends.
#         """
#         delta = relativedelta(days=0)
#         sa_delta = relativedelta(days=2)
#         su_delta = relativedelta(days=1)
#         if dt.weekday() == SA.weekday and SA not in facility.days:
#             delta = sa_delta
#         if dt.weekday() == SU.weekday and SU not in facility.days:
#             delta = su_delta
#         return dt + delta

#     @property
#     def extra_create_appointment_options(self):
#         """User can add extra options for appointment.objects.create.
#         """
#         return {}

    def update_or_create_appointment(self, visit, suggested_datetime,
                                     timepoint_datetime):
        """Updates or creates an appointment for this subject
        for the visit.
        """
        appointment_creator = self.appointment_creator_cls(
            model_obj=self,
            visit=visit,
            suggested_datetime=suggested_datetime,
            timepoint_datetime=timepoint_datetime)
        return appointment_creator.appointment

    def delete_unused_appointments(self):
        appointments = self.appointment_model.objects.filter(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name)
        for appointment in appointments:
            try:
                appointment.delete()
            except ProtectedError:
                pass
        return None

    class Meta:
        abstract = True
        visit_schedule_name = None
