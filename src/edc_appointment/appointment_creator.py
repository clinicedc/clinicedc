from datetime import timedelta
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.timezone import is_naive


class CreateAppointmentError(Exception):
    pass


class AppointmentCreatorNaiveDatetime(Exception):
    pass


class AppointmentCreator:

    def __init__(self, suggested_datetime=None, timepoint_datetime=None,
                 model_obj=None, visit=None, visit_code_sequence=None, facility_name=None,
                 subject_identifier=None, visit_schedule_name=None, schedule_name=None,
                 visit_code=None, visit_timepoint=None, appointment_model=None,
                 ):
        self._appointment = None
        self.appointment_model = appointment_model
        if suggested_datetime and is_naive(suggested_datetime):
            raise AppointmentCreatorNaiveDatetime(
                f'Naive datetime not allowed. See suggested_datetime. '
                f'Got {suggested_datetime}')
        else:
            self.suggested_datetime = suggested_datetime
        if timepoint_datetime and is_naive(timepoint_datetime):
            raise AppointmentCreatorNaiveDatetime(
                f'Naive datetime not allowed. See timepoint_datetime. '
                f'Got {timepoint_datetime}')
        else:
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
    def options(self):
        """Returns default options to "get" an existing
        appointment model instance.
        """
        return dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit_code,
            visit_code_sequence=self.visit_code_sequence,
            timepoint=self.visit_timepoint,
            facility_name=self.facility_name)

    def _create(self):
        """Returns a newly created appointment model instance.
        """
        try:
            with transaction.atomic():
                appointment = self.appointment_model_cls.objects.create(
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

    def _update(self, appointment=None):
        """Returns an updated appointment model instance.
        """
        if (appointment.timepoint_datetime
                - self.suggested_datetime != timedelta(0, 0, 0)):
            appointment.appt_datetime = self.suggested_datetime
            appointment.timepoint_datetime = self.timepoint_datetime
            appointment.save()
        return appointment

    @property
    def appointment_model_cls(self):
        if not self.appointment_model:
            app_config = django_apps.get_app_config('edc_appointment')
            self.appointment_model = app_config.appointment_model
        return django_apps.get_model(self.appointment_model)

    @property
    def default_appt_type(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.default_appt_type
