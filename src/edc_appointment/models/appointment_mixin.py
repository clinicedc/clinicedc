from django.db import models

from edc_configuration.models import GlobalConfiguration
from edc_visit_schedule.models import VisitDefinition, ScheduleGroup

from ..exceptions import AppointmentCreateError

from .appointment import Appointment
from .appointment_date_helper import AppointmentDateHelper
from .subject_configuration import SubjectConfiguration


class AppointmentMixin(models.Model):

    """ Model Mixin to add methods to create appointments.

    Such models may be listed by name in the ScheduledGroup model and thus
    trigger the creation of appointments.

    """

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
        appointments = self.create_all(using=using)
        self.post_prepare_appointments(appointments, using)

    def create_all(self, base_appt_datetime=None, using=None,
                   visit_definitions=None, dashboard_type=None):
        """Creates appointments for a registered subject based on a list
        of visit definitions for the given membership form instance.

            1. Only create for visit_instance = 0
            2. If appointment exists, just update the appt_datetime

            visit_definition contains the schedule group which contains the membership form
        """
        appointments = []
        default_appt_type = self.get_default_appt_type(self.registered_subject)
        for visit_definition in self.visit_definitions_for_schedule_group(self._meta.model_name):
            appointment = self.update_or_create_appointment(
                self.registered_subject,
                base_appt_datetime or self.get_registration_datetime(),
                visit_definition,
                default_appt_type,
                dashboard_type,
                using)
            appointments.append(appointment)
        return appointments

    def get_default_appt_type(self, registered_subject):
        """Returns the default appointment type fetched from either the subject
        specific setting or the global setting."""
        default_appt_type = 'clinic'
        try:
            default_appt_type = SubjectConfiguration.objects.get(
                subject_identifier=registered_subject.subject_identifier).default_appt_type
        except SubjectConfiguration.DoesNotExist:
            try:
                default_appt_type = GlobalConfiguration.objects.get_attr_value('default_appt_type')
            except GlobalConfiguration.DoesNotExist:
                pass
        except AttributeError as e:
            if '\'NoneType\' object has no attribute \'subject_identifier\'' not in str(e):
                raise
            else:
                pass
        return default_appt_type

    def visit_definitions_for_schedule_group(self, model_name):
        """Returns a visit_definition queryset for this membership form's schedule_group."""
        # VisitDefinition = get_model('edc_visit_schedule', 'VisitDefinition')
        schedule_group = self.schedule_group(model_name)
        visit_definitions = VisitDefinition.objects.filter(
            schedule_group=schedule_group).order_by('time_point')
        if not visit_definitions:
            raise AppointmentCreateError(
                'No visit_definitions found for membership form class {0} '
                'in schedule group {1}. Expected at least one visit '
                'definition to be associated with schedule group {1}.'.format(
                    model_name, schedule_group))
        return visit_definitions

    def update_or_create_appointment(self, registered_subject, registration_datetime, visit_definition,
                                     default_appt_type, dashboard_type, using):
        """Updates or creates an appointment for this registered subject for the visit_definition."""
        appt_datetime = self.new_appointment_appt_datetime(
            registered_subject=registered_subject,
            registration_datetime=registration_datetime,
            visit_definition=visit_definition)
        try:
            appointment = Appointment.objects.using(using).get(
                registered_subject=registered_subject,
                visit_definition=visit_definition,
                visit_instance='0')
            td = appointment.best_appt_datetime - appt_datetime
            if td.days == 0 and abs(td.seconds) > 59:
                # the calculated appointment date does not match
                # the best_appt_datetime (not within 59 seconds)
                # which means you changed the date on the membership form and now
                # need to correct the best_appt_datetime
                appointment.appt_datetime = appt_datetime
                appointment.best_appt_datetime = appt_datetime
                appointment.save(using, update_fields=['appt_datetime', 'best_appt_datetime'])
        except Appointment.DoesNotExist:
            appointment = Appointment.objects.using(using).create(
                registered_subject=registered_subject,
                visit_definition=visit_definition,
                visit_instance='0',
                appt_datetime=appt_datetime,
                timepoint_datetime=appt_datetime,
                dashboard_type=dashboard_type,
                appt_type=default_appt_type)
        return appointment

    def schedule_group(self, model_name):
        """Returns the schedule_group for this membership_form."""
        try:
            schedule_group = ScheduleGroup.objects.get(
                membership_form__content_type_map__model=model_name)
        except ScheduleGroup.DoesNotExist:
            raise ScheduleGroup.DoesNotExist(
                'Cannot prepare appointments for membership form. '
                'Membership form \'{}\' not found in ScheduleGroup. '
                'See the visit schedule configuration.'.format(model_name))
        return schedule_group

    def new_appointment_appt_datetime(
            self, registered_subject, registration_datetime, visit_definition):
        """Calculates and returns the appointment date for new appointments."""
        appointment_date_helper = AppointmentDateHelper(Appointment)
        if visit_definition.time_point == 0:
            appt_datetime = appointment_date_helper.get_best_datetime(
                registration_datetime, registered_subject.study_site)
        else:
            appt_datetime = appointment_date_helper.get_relative_datetime(
                registration_datetime, visit_definition)
        return appt_datetime

    class Meta:
        abstract = True
