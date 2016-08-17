from django.apps import apps as django_apps
from django.db import models

from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .appointment_date_helper import AppointmentDateHelper


class AppointmentMixin(models.Model):

    """ Model Mixin to add methods to create appointments.

    Such models may be listed by name in the ScheduledGroup model and thus
    trigger the creation of appointments.

    """
    @property
    def appointment_app_config(self):
        return django_apps.get_app_config('edc_appointment')

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').appointment_model

    def pre_prepare_appointments(self, using):
        """Users may override to add functionality before creating appointments."""
        return None

    def post_prepare_appointments(self, appointments, using):
        """Users may override to add functionality after creating appointments."""
        return None

    def prepare_appointments(self, using):
        """Creates all appointments linked to this instance.

        Calls :func:`pre_prepare_appointments` and :func:`post_prepare_appointments`
        """
        self.pre_prepare_appointments(using)
        appointments = self.create_all()
        self.post_prepare_appointments(appointments, using)
        return appointments

    @property
    def visit_schedule(self):
        return site_visit_schedules.get_visit_schedule(
            self._meta.app_label, self._meta.model_name)

    @property
    def schedule(self):
        return self.visit_schedule.get_schedule(
            app_label=self._meta.app_label, model_name=self._meta.model_name)

    def create_all(self, base_appt_datetime=None):
        """Creates appointments. """
        appointments = []
        default_options = dict(
            registration_datetime=base_appt_datetime or self.get_registration_datetime(),
            default_appt_type=self.appointment_app_config.default_appt_type)
        for visit in self.schedule.visits.values():
            appointment = self.update_or_create_appointment(visit=visit, **default_options)
            appointments.append(appointment)
        return appointments

    def update_or_create_appointment(self, visit=None, subject_identifier=None, registration_datetime=None,
                                     default_appt_type=None, dashboard_type=None):
        """Updates or creates an appointment for this subject for the visit."""
        appt_datetime = self.new_appointment_appt_datetime(registration_datetime, visit)
        try:
            appointment = self.appointment_model.objects.get(
                subject_identifier=subject_identifier,
                visit_schedule_name=self.visit_schedule.name,
                schedule_name=self.schedule.name,
                visit_code=visit.code,
                visit_code_sequence=0)
            td = appointment.best_appt_datetime - appt_datetime
            if td.days == 0 and abs(td.seconds) > 59:
                # the calculated appointment date does not match
                # the best_appt_datetime (not within 59 seconds)
                # which means you changed the date on the membership form and now
                # need to correct the best_appt_datetime
                appointment.appt_datetime = appt_datetime
                appointment.best_appt_datetime = appt_datetime
                appointment.save(update_fields=['appt_datetime', 'best_appt_datetime'])
        except self.appointment_model.DoesNotExist:
            appointment = self.appointment_model.objects.create(
                subject_identifier=subject_identifier,
                visit_schedule_name=self.visit_schedule.name,
                schedule_name=self.schedule.name,
                visit_code=visit.code,
                visit_code_sequence=0,
                appt_datetime=appt_datetime,
                timepoint_datetime=appt_datetime,
                dashboard_type=dashboard_type,
                appt_type=default_appt_type)
        return appointment

    def visit_definitions_for_schedule(self, model_name):
        """Returns a visit_definitions for this membership form's schedule."""
        schedule = site_visit_schedules.get_visit_schedule(model_name)
        return schedule.visit_definitions

    @property
    def date_helper(self):
        return AppointmentDateHelper(self.appointment_model)

    def new_appointment_appt_datetime(self, registration_datetime, visit):
        """Calculates and returns the appointment date for new appointments."""
        if visit.time_point == 0:
            appt_datetime = self.date_helper.get_best_datetime(
                registration_datetime)
        else:
            appt_datetime = self.get_relative_datetime(
                registration_datetime, visit.code)
        return appt_datetime

    def get_relative_datetime(self, base_appt_datetime, visit):
        """ Returns appointment datetime relative to the base_appointment_datetime."""
        appt_datetime = base_appt_datetime + self.schedule.relativedelta_from_base(visit)
        return self.date_helper.get_best_datetime(appt_datetime, base_appt_datetime.isoweekday())

    class Meta:
        abstract = True
