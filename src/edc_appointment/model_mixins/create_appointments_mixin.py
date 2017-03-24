import arrow

from datetime import timedelta
from dateutil.relativedelta import relativedelta, SA, SU

from django.apps import apps as django_apps
from django.db import models, transaction
from django.db.models import options
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError

from ..exceptions import CreateAppointmentError


if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class CreateAppointmentsMixin(models.Model):
    """ Model Mixin to add fields and methods to an enrollment
    model to create appointments on post_save.

    Requires model mixins VisitScheduleFieldsModelMixin,
    VisitScheduleMethodsModelMixin.
    """
    facility_name = models.CharField(
        verbose_name='To which facility is this subject being enrolled?',
        max_length=25,
        default='clinic',
        help_text='The facility name is need when scheduling appointments')

    @property
    def appointment_model(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.model

    @property
    def default_appt_type(self):
        app_config = django_apps.get_app_config('edc_appointment')
        return app_config.default_appt_type

    @property
    def extra_create_appointment_options(self):
        """User can add extra options for appointment.objects.create.
        """
        return {}

    def create_appointments(self, base_appt_datetime=None):
        """Creates appointments when called by post_save signal.

        Timepoint datetimes are adjusted according to the available
        days in the facility.
        """
        app_config = django_apps.get_app_config('edc_appointment')
        appointments = []
        base_appt_datetime = base_appt_datetime or self.report_datetime
        base_appt_datetime = arrow.Arrow.fromdatetime(
            base_appt_datetime, base_appt_datetime.tzinfo).to('utc').datetime
        facility = app_config.get_facility(self.facility_name)
        timepoint_datetimes = self.timepoint_datetimes(
            base_appt_datetime, self.schedule)
        taken_datetimes = []
        for visit, timepoint_datetime in timepoint_datetimes:
            adjusted_timepoint_datetime = self.move_to_facility_day(
                facility, timepoint_datetime)
            available_datetime = facility.available_datetime(
                adjusted_timepoint_datetime, taken_datetimes=taken_datetimes)
            appointment = self.update_or_create_appointment(
                visit, available_datetime, timepoint_datetime)
            appointments.append(appointment)
            taken_datetimes.append(available_datetime)
        return appointments

    def move_to_facility_day(self, facility, dt, forward_only=None):
        """Move a date forward off of a weekend unless app_config
        includes weekends.
        """
        delta = relativedelta(days=0)
        sa_delta = relativedelta(days=2)
        su_delta = relativedelta(days=1)
        if dt.weekday() == SA.weekday and SA not in facility.days:
            delta = sa_delta
        if dt.weekday() == SU.weekday and SU not in facility.days:
            delta = su_delta
        return dt + delta

    def update_or_create_appointment(self, visit, available_datetime,
                                     timepoint_datetime):
        """Updates or creates an appointment for this subject
        for the visit.
        """
        options = dict(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule.name,
            schedule_name=self.schedule.name,
            visit_code=visit.code,
            visit_code_sequence=0,
            timepoint=visit.timepoint,
            facility_name=self.facility_name)
        try:
            appointment = self.appointment_model.objects.get(**options)
            if (appointment.timepoint_datetime
                    - available_datetime != timedelta(0, 0, 0)):
                appointment.appt_datetime = available_datetime
                appointment.timepoint_datetime = timepoint_datetime
            # update_fields=['appt_datetime', 'timepoint_datetime'])
            appointment.save()
        except self.appointment_model.DoesNotExist:
            try:
                with transaction.atomic():
                    options.update(self.extra_create_appointment_options)
                    appointment = self.appointment_model.objects.create(
                        **options,
                        timepoint_datetime=timepoint_datetime,
                        appt_datetime=available_datetime,
                        appt_type=self.default_appt_type)
            except IntegrityError as e:
                raise CreateAppointmentError(
                    'An \'IntegrityError\' was raised while trying to '
                    'create an appointment for model \'{}\'. Got {}. '
                    'Options were {}'. format(
                        self._meta.label_lower, str(e), options))
        return appointment

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
