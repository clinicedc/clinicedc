from datetime import date

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Max

from edc_configuration.models import GlobalConfiguration, SubjectConfiguration
from edc_constants.constants import NEW
from edc_visit_schedule.models import VisitDefinition, ScheduleGroup
from edc_visit_tracking.constants import VISIT_REASON_NO_FOLLOW_UP_CHOICES

# from edc_entry.helpers import ScheduledEntryMetaDataHelper

from edc_constants.constants import IN_PROGRESS, COMPLETE, INCOMPLETE, CANCELLED
from ..exceptions import AppointmentCreateError, AppointmentStatusError

from .appointment_date_helper import AppointmentDateHelper


class AppointmentHelper(object):

    def __init__(self):
        self.appointment_date_helper = AppointmentDateHelper()
        self.appointment_cls = django_apps.get_model('edc_appointment', 'edc_appointment')
        self.scheduled_entry_meta_data_cls = django_apps.get_model('entry_meta_data', 'ScheduledEntryMetaData')
        self.requisition_meta_data_cls = django_apps.get_model('entry_meta_data', 'RequisitionMetaData')

    def create_all(self, registered_subject, model_name, using=None,
                   base_appt_datetime=None, dashboard_type=None, source=None,
                   visit_definitions=None, verbose=False):
        """Creates appointments for a registered subject based on a list
        of visit definitions if given model_name is a member of a schedule group.

            Args:
                registered_subject: current subject
                model_name: model of the member
                dashboard_type:

            1. Only create for visit_instance = 0
            2. If edc_appointment exists, just update the appt_datetime

            visit_definition contains schedule group contains member models
        """
        appointments = []
        self.registered_subject = registered_subject
        try:
            schedule_group = ScheduleGroup.objects.get(member__content_type_map__model=model_name)
            model = schedule_group.member.content_type_map.model_class()
            try:
                if not base_appt_datetime:
                    instance = model.objects.get(registered_subject=self.registered_subject)
                    base_appt_datetime = instance.get_registration_datetime()
            except model.DoesNotExist:
                raise model.DoesNotExist(
                    'While creating appointments, expected to find an instance of model '
                    '{0} belonging to schedule group {1}.'.format(
                        model, schedule_group))

            visit_definitions = visit_definitions or VisitDefinition.objects.filter(
                schedule_group=schedule_group).order_by('time_point')
            Appointment = django_apps.get_model('edc_appointment', 'edc_appointment')
            if not visit_definitions:
                raise AppointmentCreateError(
                    'No visit_definitions found for schedule group member {0} '
                    'in schedule group {1}. Expected at least one visit '
                    'definition to be associated with schedule group {1}.'.format(
                        model, schedule_group))
            for visit_definition in visit_definitions:
                # calculate the edc_appointment date for new appointments
                if visit_definition.time_point == 0:
                    appt_datetime = self.appointment_date_helper.get_best_datetime(
                        base_appt_datetime, registered_subject.study_site)
                else:
                    appt_datetime = self.appointment_date_helper.get_relative_datetime(
                        base_appt_datetime, visit_definition)
                try:
                    appointment = Appointment.objects.using(using).get(
                        registered_subject=registered_subject,
                        visit_definition=visit_definition,
                        visit_instance='0')
                    td = appointment.best_appt_datetime - appt_datetime
                    if td.days == 0 and abs(td.seconds) > 59:
                        # the calculated edc_appointment date does not match
                        # the best_appt_datetime (not within 59 seconds)
                        # which means you changed the date on the member model and now
                        # need to correct the best_appt_datetime
                        appointment.appt_datetime = appt_datetime
                        appointment.best_appt_datetime = appt_datetime
                        appointment.save(using)
                except Appointment.DoesNotExist:
                    appointment = Appointment.objects.using(using).create(
                        registered_subject=registered_subject,
                        visit_definition=visit_definition,
                        visit_instance='0',
                        appt_datetime=appt_datetime,
                        timepoint_datetime=appt_datetime,
                        dashboard_type=dashboard_type,
                        appt_type=self.default_appt_type)
                appointments.append(appointment)
        except ScheduleGroup.DoesNotExist:
            pass
        return appointments

    def delete_for_instance(self, model_instance, using=None):
        """ Delete appointments for this registered_subject for this
        model_instance but only if visit report not yet submitted """
        visit_definitions = VisitDefinition.objects.list_all_for_model(
            model_instance.registered_subject, model_instance._meta.object_name.lower())
        # only delete appointments without a visit model
        appointments = self.appointment_cls.objects.using(using).filter(
            registered_subject=model_instance.registered_subject, visit_definition__in=visit_definitions)
        count = 0
        visit_model = model_instance.get_visit_model_cls(model_instance)
        # find the most recent visit model instance and delete any appointments after that
        for appointment in appointments:
            if not visit_model.objects.using(using).filter(appointment=appointment):
                appointment.delete()
                count += 1
        for appointment in appointments:
            if not visit_model.objects.using(using).filter(appointment=appointment):
                appointment.delete()
                count += 1
        return count

    def create_next_instance(self, base_appointment_instance, next_appt_datetime, using=None):
        """ Creates a continuation edc_appointment given the base edc_appointment
        instance (.0) and the next appt_datetime """
        appointment = base_appointment_instance
        if not self.appointment_cls.objects.using(using).filter(
                registered_subject=appointment.registered_subject,
                visit_definition=appointment.visit_definition,
                appt_datetime=next_appt_datetime):
            aggr = self.appointment_cls.objects.using(using).filter(
                registeredsubject=appointment.registered_subject,
                visit_definition=appointment.visit_definition
            ).aggregate(Max('visit_instance'))
            if aggr:
                # check if there are rules to determine a better appt_datetime
                appt_datetime = self.appointment_date_helper.get_best_datetime(
                    next_appt_datetime, appointment.registered_subject.study_site)
                next_visit_instance = int(aggr['visit_instance__max'] + 1.0)
                self.appointment_cls.objects.using(using).create(
                    registered_subject=appointment.registered_subject,
                    visit_definition=appointment.visit_definition,
                    visit_instance=str(next_visit_instance),
                    appt_datetime=appt_datetime)

    def show_scheduled_entries(self, appointment, visit_instance):
        try:
            visit_reason_no_follow_up_choices = visit_instance.get_visit_reason_no_follow_up_choices()
        except AttributeError:
            visit_reason_no_follow_up_choices = VISIT_REASON_NO_FOLLOW_UP_CHOICES
        show_scheduled_entries = (
            visit_instance.reason.lower() not in [
                x.lower() for x in visit_reason_no_follow_up_choices.values()])
        # possible conditions that override above
        # subject is at the off study visit (lost)
        if visit_instance.reason.lower() in visit_instance.get_off_study_reason():
            visit_date = date(visit_instance.report_datetime.year,
                              visit_instance.report_datetime.month,
                              visit_instance.report_datetime.day)
            if visit_instance.get_off_study_cls().objects.filter(
                    registered_subject=appointment.registered_subject, offstudy_date=visit_date):
                # has an off study form completed on same day as visit
                off_study_instance = visit_instance.get_off_study_cls().objects.get(
                    registered_subject=appointment.registered_subject, offstudy_date=visit_date)
                show_scheduled_entries = off_study_instance.show_scheduled_entries_on_off_study_date()
        return show_scheduled_entries

    def check_appt_status(self, appointment, using):
        """Checks the appt_status relative to the visit tracking form and ScheduledEntryMetaData.
        """
        # for an existing edc_appointment, check if there is a visit tracking form already on file
        if not appointment.visit_definition.visit_tracking_content_type_map:
            raise ImproperlyConfigured(
                'Unable to determine the visit tracking model. '
                'Update bhp_visit.visit_definition {0} and select '
                'the correct visit model.'.format(appointment.visit_definition))
        if not appointment.visit_definition.visit_tracking_content_type_map.model_class().objects.filter(
                appointment=appointment):
            # no visit tracking, can only be New or Cqncelled
            if appointment.appt_status not in [NEW, CANCELLED]:
                appointment.appt_status = NEW
        else:
            # have visit tracking, can only be Done, Incomplete, In Progress
            visit_model_instance = \
                appointment.visit_definition.visit_tracking_content_type_map.model_class().objects.get(
                    appointment=appointment)
            # scheduled_entry_helper = ScheduledEntryMetaDataHelper(appointment, visit_model_instance)
            if not self.show_scheduled_entries():
                # visit reason implies no data will be collected, so set edc_appointment to Done
                appointment.appt_status = COMPLETE
            else:
                # set to in progress, if not already set
                if appointment.appt_status in [COMPLETE, INCOMPLETE]:
                    # test if Done or Incomplete

                    if ((self.scheduled_entry_meta_data_cls.objects.filter(
                            appointment=appointment, entry_status__iexact=NEW).exists() or
                         self.requisition_meta_data_cls.objects.filter(
                            appointment=appointment, entry_status__iexact=NEW).exists())):
                        appointment.appt_status = INCOMPLETE
                    else:
                        appointment.appt_status = COMPLETE
                elif appointment.appt_status in [NEW, CANCELLED, IN_PROGRESS]:
                    appointment.appt_status = IN_PROGRESS
                    # only one edc_appointment can be "in_progress", so look for any others in progress and change
                    # to Done or Incomplete, depending on ScheduledEntryMetaData (if any NEW => incomplete)
                    for appt in self.appointment_cls.objects.filter(
                            registered_subject=appointment.registered_subject, appt_status=IN_PROGRESS).exclude(
                                pk=appointment.pk):
                        if (self.scheduled_entry_meta_data_cls.objects.filter(
                                appointment=appointment, entry_status__iexact=NEW).exists() or
                                self.requisition_meta_data_cls.objects.filter(
                                    appointment=appointment, entry_status__iexact=NEW).exists()):
                            # there are NEW forms
                            if appt.appt_status != INCOMPLETE:
                                appt.appt_status = INCOMPLETE
                                # call raw_save to avoid coming back to this method.
                                appt.raw_save(using)
                        else:
                            # all forms are KEYED or NOT REQUIRED
                            if appt.appt_status != COMPLETE:
                                appt.appt_status = COMPLETE
                                # call raw_save to avoid coming back to this method.
                                appt.raw_save(using)
                else:
                    raise AppointmentStatusError(
                        'Did not expect appt_status == \'{0}\''.format(appointment.appt_status))
        return appointment

    @property
    def default_appt_type(self, registered_subject):
        """Returns the default edc_appointment date fetched from either the subject
        specific setting or the global setting."""
        default_appt_type = None
        try:
            default_appt_type = SubjectConfiguration.objects.get(
                subject_identifier=registered_subject.subject_identifier).default_appt_type
        except SubjectConfiguration.DoesNotExist:
            try:
                default_appt_type = GlobalConfiguration.objects.get_attr_value('default_appt_type')
            except GlobalConfiguration.DoesNotExist:
                pass
        return default_appt_type
