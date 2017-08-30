from datetime import timedelta
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError


class CreateAppointmentError(Exception):
    pass


class AppointmentCreator:

    def __init__(self, model_obj=None, visit=None, available_datetime=None,
                 timepoint_datetime=None, visit_code_sequence=None):
        self.model_obj = model_obj
        self.visit = visit
        self.available_datetime = available_datetime
        self.timepoint_datetime = timepoint_datetime
        self.subject_identifier = model_obj.subject_identifier
        self.visit_schedule = model_obj.visit_schedule
        self.schedule = model_obj.schedule
        self.visit_code_sequence = visit_code_sequence or 0
        self.facility_name = model_obj.facility_name

    @property
    def options(self):
        return dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit_code=self.visit.code,
            visit_code_sequence=self.visit_code_sequence,
            timepoint=self.visit.timepoint,
            facility_name=self.facility_name)

    def update_or_create(self):
        """Returns an appointment instance that is created or
        updated.
        """
        try:
            appointment = self.appointment_model.objects.get(**self.options)
            if (appointment.timepoint_datetime
                    - self.available_datetime != timedelta(0, 0, 0)):
                appointment.appt_datetime = self.available_datetime
                appointment.timepoint_datetime = self.timepoint_datetime
            appointment.save()
        except ObjectDoesNotExist:
            try:
                with transaction.atomic():
                    appointment = self.appointment_model.objects.create(
                        **self.options,
                        timepoint_datetime=self.timepoint_datetime,
                        appt_datetime=self.available_datetime,
                        appt_type=self.default_appt_type)
            except IntegrityError as e:
                raise CreateAppointmentError(
                    'An \'IntegrityError\' was raised while trying to '
                    'create an appointment for model \'{}\'. Got {}. '
                    'Options were {}'. format(
                        self._meta.label_lower, str(e), self.options))
        return appointment

    @property
    def appointment_model(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.model

    @property
    def default_appt_type(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.default_appt_type
