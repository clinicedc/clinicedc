from datetime import timedelta
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError


class CreateAppointmentError(Exception):
    pass


class AppointmentCreator:

    def __init__(self, suggested_datetime=None, timepoint_datetime=None,
                 model_obj=None, visit=None, visit_code_sequence=None, facility_name=None,
                 subject_identifier=None, visit_schedule_name=None, schedule_name=None,
                 visit_code=None, visit_timepoint=None):
        self.suggested_datetime = suggested_datetime
        self.timepoint_datetime = timepoint_datetime
        if model_obj:
            self.subject_identifier = model_obj.subject_identifier
            self.visit_schedule_name = model_obj.visit_schedule.name
            self.schedule_name = model_obj.schedule.name
            self.facility_name = model_obj.facility_name
        else:
            self.subject_identifier = subject_identifier
            self.visit_schedule_name = visit_schedule_name
            self.schedule_name = schedule_name
            self.facility_name = facility_name
        if visit:
            self.visit_code = visit.code
            self.visit_timepoint = visit.timepoint
        else:
            self.visit_code = visit_code
            self.visit_timepoint = visit_timepoint
        self.visit_code_sequence = visit_code_sequence or 0

    def __repr__(self):
        return (f'{self.__class__.__name__}(subject_identifier={self.subject_identifier}, '
                'visit_code={self.visit_code})')

    def __str__(self):
        return self.subject_identifier

    @property
    def options(self):
        return dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit_code,
            visit_code_sequence=self.visit_code_sequence,
            timepoint=self.visit_timepoint,
            facility_name=self.facility_name)

    def update_or_create(self):
        """Returns an appointment instance that is created or
        updated.
        """
        try:
            appointment = self.appointment_model.objects.get(**self.options)
            if (appointment.timepoint_datetime
                    - self.suggested_datetime != timedelta(0, 0, 0)):
                appointment.appt_datetime = self.suggested_datetime
                appointment.timepoint_datetime = self.timepoint_datetime
            appointment.save()
        except ObjectDoesNotExist:
            try:
                with transaction.atomic():
                    appointment = self.appointment_model.objects.create(
                        **self.options,
                        timepoint_datetime=self.timepoint_datetime,
                        appt_datetime=self.suggested_datetime,
                        appt_type=self.default_appt_type)
            except IntegrityError as e:
                raise CreateAppointmentError(
                    f'An \'IntegrityError\' was raised while trying to '
                    f'create an appointment for model \'{self.model_obj._meta.label_lower}\'. '
                    f'Got {e}. Options were {self.options}')
        return appointment

    @property
    def appointment_model(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.model

    @property
    def default_appt_type(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.default_appt_type
