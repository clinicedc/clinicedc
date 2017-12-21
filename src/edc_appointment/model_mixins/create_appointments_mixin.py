import arrow

from django.apps import apps as django_apps
from django.db import models
from django.db.models import options
from django.db.models.deletion import ProtectedError
from edc_facility import FacilityError

from ..appointment_creator import AppointmentCreator, CreateAppointmentError


if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class CreateAppointmentsMixin(models.Model):
    """ Model Mixin to add fields and methods to an enrollment
    model to create appointments on post_save.

    Requires model mixins VisitScheduleFieldsModelMixin,
    VisitScheduleMethodsModelMixin.
    """

    appointment_creator_cls = AppointmentCreator

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
        timepoint_dates = self.schedule.visits.timepoint_dates(
            dt=base_appt_datetime)
        for visit, timepoint_datetime in timepoint_dates.items():
            try:
                facility = app_config.get_facility(visit.facility_name)
            except FacilityError as e:
                raise CreateAppointmentError(
                    f'{e} See {repr(visit)}. Got facility_name={visit.facility_name}')
            appointment = self.update_or_create_appointment(
                visit=visit,
                taken_datetimes=taken_datetimes,
                timepoint_datetime=timepoint_datetime,
                facility=facility)
            appointments.append(appointment)
            taken_datetimes.append(appointment.appt_datetime)
        return appointments

    def update_or_create_appointment(self, **kwargs):
        """Updates or creates an appointment for this subject
        for the visit.
        """
        appointment_creator = self.appointment_creator_cls(
            model_obj=self, **kwargs)
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
