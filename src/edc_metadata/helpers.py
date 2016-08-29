from django.apps import apps as django_apps
from django.core.exceptions import FieldError, ValidationError

from edc_base.utils import convert_from_camel
from edc_constants.constants import YES

edc_visit_tracking_app_config = django_apps.get_app_config('edc_visit_tracking')


class BaseMetaDataHelper(object):
    """ Base class for all classes that manage the entry state
    of additional, scheduled and unscheduled data."""

    entry_attr = None

    def __init__(self, appointment, visit_instance=None, visit_model_attrname=None):
        self.appointment = appointment
        self.visit_model = self.appointment.visit_definition.visit_model
        self.visit_model_attrname = visit_model_attrname or convert_from_camel(self.visit_model._meta.object_name)
        self.visit_instance = visit_instance

    def __repr__(self):
        return 'BaseMetaDataHelper({0.instance!r})'.format(self)

    def __str__(self):
        return '({0.instance!r})'.format(self)

    @property
    def entry_model(self):
        return django_apps.get_model('edc_meta_data', self.entry_attr.replace('_', ''))

    @property
    def visit_model_attrname(self):
        return self._visit_model_attrname

    @visit_model_attrname.setter
    def visit_model_attrname(self, attrname):
        self._visit_model_attrname = attrname or convert_from_camel(self.visit_model._meta.object_name)

    @property
    def visit_instance(self):
        return self._visit_instance

    @visit_instance.setter
    def visit_instance(self, model_or_instance):
        if model_or_instance:
            if model_or_instance._meta.model_name != self.visit_model._meta.model_name:
                raise ValueError(
                    '{} expected the visit instance to be an instance of \'{}\' '
                    'as specified in the visit definition. '
                    'Got \'{}\''.format(self.__class__.__name__,
                                        self.visit_model.__name__,
                                        model_or_instance.__class__.__name__))
        try:
            self._visit_instance = self.visit_model.objects.get(appointment=self.appointment)
        except AttributeError as e:
            if 'Manager isn\'t accessible via' not in str(e):
                raise AttributeError(str(e))
            self._visit_instance = model_or_instance

    @property
    def appointment_zero(self):
        if not self.appointment.visit_instance == '0':
            Appointment = self.appointment.__class__
            self._appointment_zero = Appointment.objects.get(
                appointment_identifier=self.appointment.appointment_identifier,
                visit_instance='0')
        else:
            self._appointment_zero = self.appointment
        return self._appointment_zero

    def show_entries(self):
        """Returns True if scheduled forms on the dashboard should be show / links active.

        If the participant os off study, the value of \'has_scheduled_data\' on the
        visit tracking for is used (YES=True, No=False)."""
        try:
            no_follow_up_reasons = self.visit_instance.get_visit_reason_no_follow_up_choices()
        except AttributeError as e:
            if 'get_visit_reason_no_follow_up_choices' not in str(e):
                raise AttributeError(str(e))
            no_follow_up_reasons = edc_visit_tracking_app_config.no_followup_reasons
        show_entries = self.visit_instance.reason not in no_follow_up_reasons
        if self.visit_instance.reason in self.visit_instance.get_off_study_reason():
            try:
                show_entries = self.visit_instance.require_crfs == YES
            except self.Visit_model.DoesNotExist:
                raise ValidationError('Visit report is required.')
        return show_entries

    def add_or_update_for_visit(self):
        """ Loops thru the list of entries configured for the visit_definition
        and calls the entry_meta_data_manager for each model.

        The visit definition comes instance."""
        for entry in self.entry_model.objects.filter(
                visit_definition=self.visit_instance.appointment.visit_definition):
            model = entry.get_model()
            model.entry_meta_data_manager.visit_instance = self.visit_instance
            try:
                model.entry_meta_data_manager.instance = model.objects.get(
                    **model.entry_meta_data_manager.query_options)
            except model.DoesNotExist:
                model.entry_meta_data_manager.instance = None
            except FieldError as e:
                raise FieldError(e, 'Try specifying the correct \'visit_attr_name\' when declaring '
                                 'the entry_meta_data_manager on {}.'.format(model))
            model.entry_meta_data_manager.update_meta_data()
            if model.entry_meta_data_manager.instance:
                model.entry_meta_data_manager.run_rule_groups()

    def get_meta_data(self, entry_status=None):
        """Returns a list of meta data instances for the given subject and appointment_zero."""
        if self.appointment_zero:
            options = {
                'appointment_identifier': self.appointment.appointment_identifier,
                'appointment_id': self.appointment_zero.pk}
            if entry_status:
                options.update({'entry_status': entry_status})
            meta_data = self.meta_data_model.objects.filter(**options).order_by(
                '{0}__entry_order'.format(self.entry_attr))
        else:
            meta_data = []
        return meta_data


class CrfMetaDataHelper(BaseMetaDataHelper):

    entry_attr = 'crf_entry'

    @property
    def meta_data_model(self):
        return django_apps.get_app_config('edc_meta_data').crf_meta_data_model


class RequisitionMetaDataHelper(BaseMetaDataHelper):

    entry_attr = 'lab_entry'

    def __repr__(self):
        return 'RequisitionMetaDataHelper({0.instance!r})'.format(self)

    def __str__(self):
        return '({0.instance!r})'.format(self)

    @property
    def meta_data_model(self):
        return django_apps.get_app_config('edc_meta_data').requisition_meta_data_model

    def get_meta_data(self, entry_status=None):
        """Returns a list of meta data instances for the given subject and appointment_zero."""
        if self.appointment:  # TODO: appointment_zero??
            options = {'appointment_id': self.appointment.pk}
            if entry_status:
                options.update({'entry_status': entry_status})
            meta_data = self.meta_data_model.objects.filter(**options).order_by(
                '{0}__entry_order'.format(self.entry_attr))
        else:
            meta_data = []
        return meta_data

    def add_or_update_for_visit(self):
        """ Loops thru the list of entries configured for the visit_definition
        and calls the entry_meta_data_manager for each model.

        The visit definition comes instance."""
        for lab_entry in self.entry_model.objects.filter(visit_definition=self.appointment.visit_definition):
            model = lab_entry.get_model()
            model.entry_meta_data_manager.visit_instance = self.visit_instance
            model.entry_meta_data_manager.target_requisition_panel = lab_entry.requisition_panel
            try:
                model.entry_meta_data_manager.instance = model.objects.get(
                    **model.entry_meta_data_manager.query_options)
            except model.DoesNotExist:
                model.entry_meta_data_manager.instance = None
            model.entry_meta_data_manager.update_meta_data()
            if model.entry_meta_data_manager.instance:
                model.entry_meta_data_manager.run_rule_groups()
