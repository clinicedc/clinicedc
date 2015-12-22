from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model, Max

from edc.apps.app_configuration.models import GlobalConfiguration
from edc.subject.subject_config.models import SubjectConfiguration
from edc_constants.constants import IN_PROGRESS, COMPLETE_APPT, INCOMPLETE, UNKEYED, NEW_APPT, CANCELLED

from ..exceptions import AppointmentCreateError, AppointmentStatusError

from .appointment_date_helper import AppointmentDateHelper


class AppointmentHelper(object):

    def create_all(self, membership_form, base_appt_datetime=None, using=None,
                   visit_definitions=None, dashboard_type=None):
        """Creates appointments for a registered subject based on a list
        of visit definitions for the given membership form instance.

            1. Only create for visit_instance = 0
            2. If appointment exists, just update the appt_datetime

            visit_definition contains the schedule group which contains the membership form
        """
        appointments = []
        default_appt_type = self.get_default_appt_type(membership_form.registered_subject)
        for visit_definition in self.visit_definitions_for_schedule_group(membership_form._meta.model_name):
            appointment = self.update_or_create_appointment(
                membership_form.registered_subject,
                base_appt_datetime or membership_form.get_registration_datetime(),
                visit_definition,
                default_appt_type,
                dashboard_type,
                using)
            appointments.append(appointment)
        return appointments

    def update_or_create_appointment(self, registered_subject, registration_datetime, visit_definition,
                                     default_appt_type, dashboard_type, using):
        """Updates or creates an appointment for this registered subject for the visit_definition."""
        Appointment = get_model('edc_appointment', 'appointment')
        appt_datetime = self.new_appointment_appt_datetime(
            registered_subject=registered_subject,
            registration_datetime=registration_datetime,
            visit_definition=visit_definition,
            appointment_model_cls=Appointment)
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
                appointment.save(using)
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

    def new_appointment_appt_datetime(
            self, registered_subject, registration_datetime, visit_definition, appointment_model_cls=None):
        """Calculates and returns the appointment date for new appointments."""
        appointment_date_helper = AppointmentDateHelper(appointment_model_cls)
        if visit_definition.time_point == 0:
            appt_datetime = appointment_date_helper.get_best_datetime(
                registration_datetime, registered_subject.study_site)
        else:
            appt_datetime = appointment_date_helper.get_relative_datetime(
                registration_datetime, visit_definition)
        return appt_datetime

    def visit_definitions_for_schedule_group(self, model_name):
        """Returns a visit_definition queryset for this membership form's schedule_group."""
        VisitDefinition = get_model('edc_visit_schedule', 'VisitDefinition')
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

    def schedule_group(self, membership_form_model_name):
        """Returns the schedule_group for this membership_form."""
        ScheduleGroup = get_model('edc_visit_schedule', 'ScheduleGroup')
        try:
            schedule_group = ScheduleGroup.objects.get(
                membership_form__content_type_map__model=membership_form_model_name)
        except ScheduleGroup.DoesNotExist:
            raise ScheduleGroup.DoesNotExist(
                'Cannot prepare appointments for membership form. '
                'Membership form \'{}\' not found in ScheduleGroup. '
                'See the visit schedule configuration.'.format(membership_form_model_name))
        return schedule_group

#     def delete_for_instance(self, model_instance, using=None):
#         """ Delete appointments for this registered_subject for this
#         model_instance but only if visit report not yet submitted """
#         visit_definitions = VisitDefinition.objects.list_all_for_model(
#             model_instance.registered_subject, model_instance._meta.object_name.lower())
#         Appointment = get_model('edc_appointment', 'appointment')
#         # only delete appointments without a visit model
#         appointments = Appointment.objects.using(using).filter(
#             registered_subject=model_instance.registered_subject, visit_definition__in=visit_definitions)
#         count = 0
#         visit_model = model_instance.get_visit_model_cls(model_instance)
#         # find the most recent visit model instance and delete any appointments after that
#         for appointment in appointments:
#             if not visit_model.objects.using(using).filter(appointment=appointment):
#                 appointment.delete()
#                 count += 1
#         for appointment in appointments:
#             if not visit_model.objects.using(using).filter(appointment=appointment):
#                 appointment.delete()
#                 count += 1
#         return count

    def create_next_instance(self, base_appointment_instance, next_appt_datetime, using=None):
        """ Creates a continuation appointment given the base appointment
        instance (.0) and the next appt_datetime """
        appointment = base_appointment_instance
        Appointment = get_model('edc_appointment', 'appointment')
        if not Appointment.objects.using(using).filter(
                registered_subject=appointment.registered_subject,
                visit_definition=appointment.visit_definition,
                appt_datetime=next_appt_datetime):
            aggr = Appointment.objects.using(using).filter(
                registeredsubject=appointment.registered_subject,
                visit_definition=appointment.visit_definition).aggregate(Max('visit_instance'))
            if aggr:
                appointment_date_helper = AppointmentDateHelper()
                # check if there are rules to determine a better appt_datetime
                appt_datetime = appointment_date_helper.get_best_datetime(
                    next_appt_datetime, appointment.registered_subject.study_site)
                next_visit_instance = int(aggr['visit_instance__max'] + 1.0)
                Appointment.objects.using(using).create(
                    registered_subject=appointment.registered_subject,
                    visit_definition=appointment.visit_definition,
                    visit_instance=str(next_visit_instance),
                    appt_datetime=appt_datetime)

    def check_appt_status(self, appointment, using):
        """Checks the appt_status relative to the visit tracking form and ScheduledEntryMetaData.
        """
        from edc.entry_meta_data.helpers import ScheduledEntryMetaDataHelper
        # for an existing appointment, check if there is a visit tracking form already on file
        if not appointment.visit_definition.visit_tracking_content_type_map:
            raise ImproperlyConfigured(
                'Unable to determine the visit tracking model. '
                'Update bhp_visit.visit_definition {0} and select '
                'the correct visit model.'.format(appointment.visit_definition))
        if not appointment.visit_definition.visit_tracking_content_type_map.model_class().objects.filter(
                appointment=appointment):
            # no visit tracking, can only be New or Cqncelled
            if appointment.appt_status not in [NEW_APPT, CANCELLED]:
                appointment.appt_status = NEW_APPT
        else:
            # have visit tracking, can only be Done, Incomplete, In Progress
            visit_model_instance = \
                appointment.visit_definition.visit_tracking_content_type_map.model_class().objects.get(
                    appointment=appointment)
            scheduled_entry_helper = ScheduledEntryMetaDataHelper(appointment, visit_model_instance)
            if not scheduled_entry_helper.show_scheduled_entries():
                # visit reason implies no data will be collected, so set appointment to Done
                appointment.appt_status = COMPLETE_APPT
            else:
                ScheduledEntryMetaData = get_model('entry_meta_data', 'ScheduledEntryMetaData')
                RequisitionMetaData = get_model('entry_meta_data', 'RequisitionMetaData')
                # set to in progress, if not already set
                if appointment.appt_status in [COMPLETE_APPT, INCOMPLETE]:
                    # test if Done or Incomplete

                    if ((ScheduledEntryMetaData.objects.filter(
                            appointment=appointment, entry_status__iexact=UNKEYED).exists() or
                         RequisitionMetaData.objects.filter(
                            appointment=appointment, entry_status__iexact=UNKEYED).exists())):
                        appointment.appt_status = INCOMPLETE
                    else:
                        appointment.appt_status = COMPLETE_APPT
                elif appointment.appt_status in [NEW_APPT, CANCELLED, IN_PROGRESS]:
                    appointment.appt_status = IN_PROGRESS
                    # only one appointment can be "in_progress", so look for any others in progress and change
                    # to Done or Incomplete, depending on ScheduledEntryMetaData (if any NEW => incomplete)
                    ScheduledEntryMetaData = get_model('entry_meta_data', 'ScheduledEntryMetaData')
                    RequisitionMetaData = get_model('entry_meta_data', 'RequisitionMetaData')
                    for appt in appointment.__class__.objects.filter(
                            registered_subject=appointment.registered_subject, appt_status=IN_PROGRESS).exclude(
                                pk=appointment.pk):
                        if (ScheduledEntryMetaData.objects.filter(
                                appointment=appointment, entry_status__iexact=UNKEYED).exists() or
                                RequisitionMetaData.objects.filter(
                                    appointment=appointment, entry_status__iexact=UNKEYED).exists()):
                            # there are NEW forms
                            if appt.appt_status != INCOMPLETE:
                                appt.appt_status = INCOMPLETE
                                # call raw_save to avoid coming back to this method.
                                appt.raw_save(using)
                        else:
                            # all forms are KEYED or NOT REQUIRED
                            if appt.appt_status != COMPLETE_APPT:
                                appt.appt_status = COMPLETE_APPT
                                # call raw_save to avoid coming back to this method.
                                appt.raw_save(using)
                else:
                    raise AppointmentStatusError(
                        'Did not expect appt_status == \'{0}\''.format(appointment.appt_status))
        return appointment

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
