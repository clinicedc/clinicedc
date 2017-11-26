from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.timezone import is_naive

from .appointment_config import AppointmentConfigError


class CreateAppointmentError(Exception):
    pass


class AppointmentCreatorError(Exception):
    pass


class AppointmentCreator:

    def __init__(self, model_obj=None, suggested_datetime=None, timepoint_datetime=None,
                 visit=None, visit_code_sequence=None, facility=None,
                 subject_identifier=None, visit_schedule_name=None, schedule_name=None,
                 default_appt_type=None):
        self._appointment = None
        self._appointment_config = None
        self._appointment_model_cls = None
        self._default_appt_type = default_appt_type
        if model_obj:
            self.subject_identifier = model_obj.subject_identifier
            self.visit_schedule_name = model_obj.visit_schedule.name
            self.schedule_name = model_obj.schedule.name
        else:
            self.subject_identifier = subject_identifier
            self.visit_schedule_name = visit_schedule_name
            self.schedule_name = schedule_name
        self.visit = visit
        self.appointment_model = visit.appointment_model
        self.visit_code_sequence = visit_code_sequence or 0
        if suggested_datetime and is_naive(suggested_datetime):
            raise ValueError(
                f'Naive datetime not allowed. {repr(self)}. '
                f'Got {suggested_datetime}')
        else:
            self.suggested_datetime = suggested_datetime
        if timepoint_datetime and is_naive(timepoint_datetime):
            raise ValueError(
                f'Naive datetime not allowed. {repr(self)}. '
                f'Got {timepoint_datetime}')
        else:
            self.timepoint_datetime = timepoint_datetime
        self.facility = facility or visit.facility or model_obj.facility
        if not self.facility:
            raise AppointmentCreatorError('Facility not defined.')
        self.appointment

    def __repr__(self):
        return (f'{self.__class__.__name__}(subject_identifier={self.subject_identifier}, '
                f'visit_code={self.visit.code})')

    def __str__(self):
        return self.subject_identifier

    @property
    def appointment(self):
        """Returns a newly created or updated appointment model instance.
        """
        if not self._appointment:
            try:
                self._appointment = self.appointment_model_cls.objects.get(
                    **self.options)
            except ObjectDoesNotExist:
                self._appointment = self._create()
            else:
                self._appointment = self._update(appointment=self._appointment)
        return self._appointment

    @property
    def available_rdate(self, dt=None):
        available_datetime = self.facility.available_rdate(dt)
        return available_datetime

    @property
    def options(self):
        """Returns default options to "get" an existing
        appointment model instance.
        """
        return dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit.code,
            visit_code_sequence=self.visit_code_sequence,
            timepoint=self.visit.timepoint)

    def _create(self):
        """Returns a newly created appointment model instance.
        """
        try:
            with transaction.atomic():
                appointment = self.appointment_model_cls.objects.create(
                    facility_name=self.facility.name,
                    timepoint_datetime=self.timepoint_datetime,
                    appt_datetime=self.appt_rdate.datetime,
                    appt_type=self.default_appt_type,
                    **self.options)
        except IntegrityError as e:
            raise CreateAppointmentError(
                f'An \'IntegrityError\' was raised while trying to '
                f'create an appointment for subject \'{self.subject_identifier}\'. '
                f'Got {e}. Options were {self.options}')
        return appointment

    def _update(self, appointment=None):
        """Returns an updated appointment model instance.
        """
        appointment.appt_datetime = self.appt_rdate.datetime
        appointment.timepoint_datetime = self.timepoint_datetime
        appointment.save()
        return appointment

    @property
    def appt_rdate(self):
        # TODO: no dates available?
        # if not appt_rdate: ???
        return self.facility.available_rdate(
            suggested_datetime=self.suggested_datetime,
            forward_delta=self.visit.rupper,
            reverse_delta=self.visit.rlower)

    @property
    def appointment_config(self):
        if not self._appointment_config:
            app_config = django_apps.get_app_config('edc_appointment')
            try:
                self._appointment_config = [
                    a for a in app_config.configurations if a.name == self.appointment_model][0]
            except IndexError as e:
                if len(app_config.configurations) == 1 and not self.appointment_model:
                    self._appointment_config = app_config.configurations[0]
                else:
                    config_names = [a.name for a in app_config.configurations]
                    raise AppointmentConfigError(
                        f'Error looking up appointment config for {self.appointment_model}. '
                        f'Got {e}. AppoinmentConfigs exist for {config_names}. '
                        f'See {app_config.configurations}. See also the visit schedule '
                        f'and or settings.DEFAULT_APPOINTMENT_MODEL.')
        return self._appointment_config

    @property
    def appointment_model_cls(self):
        """Returns the appointment model class.
        """
        if not self._appointment_model_cls:
            self._appointment_model_cls = self.appointment_config.model_cls
        return self._appointment_model_cls

    @property
    def default_appt_type(self):
        """Returns a string that is the default appointment
        type, e.g. 'clinic'.
        """
        if not self._default_appt_type:
            self._default_appt_type = self.appointment_config.appt_type
        return self._default_appt_type
