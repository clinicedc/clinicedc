from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_base.utils import convert_from_camel
from edc_visit_tracking.constants import MISSED_VISIT, LOST_VISIT

from .constants import REQUIRED, NOT_REQUIRED, KEYED


class BaseMetaDataManager(models.Manager):

    """Base class for Crf manager methods 'entry_meta_data_manager = '. See below.

    Creates, updates or deletes meta data that tracks the
    entry status of models for a given visit."""

    meta_data_model = None
    entry_attr = None
    # list of visit reasons where meta data should not be created
    skip_create_visit_reasons = [MISSED_VISIT, LOST_VISIT, 'vital status']
    may_delete_entry_status = [REQUIRED, NOT_REQUIRED]

    def __init__(self, visit_model, visit_attr_name=None):
        self.name = None
        self._instance = None
        self._status = None
        self._meta_data_instance = None
        self._appointment_zero = None
        self._visit_instance = None
        self.visit_model = visit_model
        self.visit_attr_name = visit_attr_name or convert_from_camel(self.visit_model._meta.object_name)
        super(BaseMetaDataManager, self).__init__()

    def __repr__(self):
        return 'BaseMetaDataManager({0.instance!r})'.format(self)

    def __str__(self):
        return '({0.instance!r})'.format(self)

    @property
    def entry_model(self):
        return django_apps.get_model('edc_meta_data', self.entry_attr.replace('_', ''))

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').appointment_model

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, instance):
        self._instance = instance

    @property
    def query_options(self):
        return {self.visit_attr_name: self.visit_instance}

    @property
    def visit_instance(self):
        return self._visit_instance

    @visit_instance.setter
    def visit_instance(self, visit_instance):
        self._visit_instance = visit_instance
        self.appointment_zero = visit_instance.appointment
        self._meta_data_instance = None

    @property
    def appointment_zero(self):
        return self._appointment_zero

    @appointment_zero.setter
    def appointment_zero(self, appointment):
        if appointment.visit_instance == '0':
            self._appointment_zero = appointment
        else:
            self._appointment_zero = self.appointment_model.objects.get(
                registered_subject=appointment.registered_subject,
                visit_definition=appointment.visit_definition,
                visit_instance='0')

    @property
    def meta_data_instance(self):
        """Returns the meta data instance using the meta data's "model" instance.

        Will be created if DoesNotExist."""
        if not self._meta_data_instance:
            try:
                self._meta_data_instance = self.meta_data_model.objects.get(**self.meta_data_query_options)
            except self.meta_data_model.DoesNotExist:
                pass  # self._meta_data_instance = self.create_meta_data()
            except ValueError:  # Cannot use None as a query value
                pass
            except AttributeError:
                pass
        return self._meta_data_instance

    @property
    def meta_data_query_options(self):
        """Returns the options to query on the meta data model."""
        return {'appointment': self.appointment_zero,
                '{0}__app_label'.format(self.entry_attr): self.model._meta.app_label,
                '{0}__model_name'.format(self.entry_attr): self.model._meta.object_name.lower()}

    def create_meta_data(self):
        raise ImproperlyConfigured('Method must be defined in the child class')

    def update_meta_data(self, change_type=None):
        """Updates the meta_data's instance.

        Calls create if meta data does not exist

        If change type is:
          * None this is being called from the post-save signal on the visit form
          * I, U, D, this is being called from the post-save signal of the model itself
          * UNKEYED or NOT_REQUIRED it's being called by a rule triggered by another model's post-save

        Called by the signal on post_save and pre_delete"""
        if self.meta_data_instance:
            if self.instance or change_type in ['I', 'U', 'D'] or self.meta_data_instance.entry_status == KEYED:
                new_status = KEYED  # (Insert, Update or no change (D or already KEYED)
                try:
                    if change_type == 'D':
                        new_status = self.get_default_entry_status()
                        self.meta_data_instance.report_datetime = None
                    self.meta_data_instance.report_datetime = self.instance.report_datetime
                except AttributeError:
                    self.meta_data_instance.report_datetime = None
            elif change_type in [REQUIRED, NOT_REQUIRED]:  # coming from a rule, cannot change if KEYED
                new_status = change_type
            if new_status and not new_status == self.meta_data_instance.entry_status:
                if new_status not in [REQUIRED, NOT_REQUIRED, KEYED]:
                    raise ValueError(
                        'Expected entry status to be set to one off {0}. Got {1}'.format(
                            [REQUIRED, NOT_REQUIRED, KEYED], new_status))
                self.meta_data_instance.entry_status = new_status
                self.meta_data_instance.save()

    def update_meta_data_from_rule(self, change_type):
        change_types = [REQUIRED, NOT_REQUIRED]
        if change_type not in change_types:
            raise ValueError('Change type must be any of {0}. Got {1}'.format(change_types, change_type))
        self.update_meta_data(change_type)

    def get_default_entry_status(self):
        try:
            default_entry_status = self.meta_data_instance.crf_entry.default_entry_status
        except AttributeError as e:
            if 'crf_entry' in str(e):
                default_entry_status = self.meta_data_instance.lab_entry.default_entry_status
        return default_entry_status

    def run_rule_groups(self):
        """Runs rule groups that use the data in this instance; that is, the model is a rule source model."""
        from edc_rule_groups.classes import site_rule_groups
        return site_rule_groups.update_rules_for_source_model(self.model, self.visit_instance)


class CrfMetaDataManager(BaseMetaDataManager):

    """Manager for requisition crf models.

    Add as a manager method on the crf model:

        entry_meta_data_manager = CrfMetaDataManager(SubjectVisit)

    """

    entry_attr = 'crf_entry'

    def __repr__(self):
        return 'CrfMetaDataManager({0.instance!r})'.format(self)

    def __str__(self):
        return '({0.instance!r})'.format(self)

    @property
    def meta_data_model(self):
        return django_apps.get_app_config('edc_meta_data').crf_meta_data_model_name

    def create_meta_data(self):
        """Creates a meta_data instance for the model at the time point (appointment)
        for the given registered_subject.

        Might return None and meta data not created based on visit reason (e.g. missed)."""
        if self.visit_instance.reason not in self.skip_create_visit_reasons:
            try:
                crf_entry = self.entry_model.objects.get(
                    app_label=self.model._meta.app_label.lower(),
                    model_name=self.model._meta.object_name.lower(),
                    visit_definition=self.appointment_zero.visit_definition)
            except self.entry_model.DoesNotExist:
                raise ImproperlyConfigured(
                    'Entry matching query does not exist in visit {0}. Model {1}.Check your'
                    ' visit schedule configuration or rule groups.'.format(
                        self.appointment_zero.visit_definition, self.model))
            return self.meta_data_model.objects.create(
                appointment=self.appointment_zero,
                registered_subject=self.appointment_zero.registered_subject,
                due_datetime=crf_entry.visit_definition.get_upper_window_datetime(
                    self.visit_instance.report_datetime),
                crf_entry=crf_entry,
                entry_status=crf_entry.default_entry_status)
        return None

    @property
    def default_entry_status(self):
        return self.meta_data_instance.entry.default_entry_status


class RequisitionMetaDataManager(BaseMetaDataManager):

    """Manager for requisition models.

    Add as a manager method on the requisition model:

        entry_meta_data_manager = RequisitionMetaDataManager(SubjectVisit)

    """

    entry_attr = 'lab_entry'

    def __init__(self, visit_model, visit_attr_name=None):
        self._target_requisition_panel = None
        super(RequisitionMetaDataManager, self).__init__(visit_model, visit_attr_name)

    def __repr__(self):
        return 'RequisitionMetaDataManager({0.instance!r})'.format(self)

    def __str__(self):
        return '({0.instance!s})'.format(self)

    @property
    def meta_data_model(self):
        return django_apps.get_app_config('edc_meta_data').requisition_meta_data_model_name

    @property
    def target_requisition_panel(self):
        return self._target_requisition_panel

    @target_requisition_panel.setter
    def target_requisition_panel(self, target_requisition_panel):
        self._target_requisition_panel = target_requisition_panel
        self._meta_data_instance = None

    @property
    def query_options(self):
        return {self.visit_attr_name: self.visit_instance, 'panel__name': self.target_requisition_panel}

    @property
    def meta_data_query_options(self):
        """Returns the options used to query the meta data model for the meta_data_instance."""
        return {'appointment': self.visit_instance.appointment,
                '{0}__app_label'.format(self.entry_attr): self.model._meta.app_label,
                '{0}__model_name'.format(self.entry_attr): self.model._meta.object_name.lower(),
                '{0}__requisition_panel__name__iexact'.format(self.entry_attr): self.target_requisition_panel}

    def create_meta_data(self):
        """Creates a meta_data instance for the model at the
        time point (appointment) for the given registered_subject.

        might return None and meta data not created based on visit reason (e.g. missed)."""
        if self.visit_instance.reason not in self.skip_create_visit_reasons:
            try:
                lab_entry = self.entry_model.objects.get(
                    app_label=self.model._meta.app_label.lower(),
                    model_name=self.model._meta.object_name.lower(),
                    visit_definition=self.visit_instance.appointment.visit_definition,
                    requisition_panel__name=self.target_requisition_panel,
                )
            except self.entry_model.DoesNotExist:
                raise ImproperlyConfigured('LabEntry matching query does not exist. Model {0}.Check your'
                                           ' visit schedule configuration or rule groups.'.format(self.model))
            if self.visit_instance.appointment.visit_instance != '0':
                entry_status = 'NOT_REQUIRED'
            else:
                entry_status = lab_entry.default_entry_status
            return self.meta_data_model.objects.create(
                appointment=self.visit_instance.appointment,
                registered_subject=self.visit_instance.appointment.registered_subject,
                due_datetime=lab_entry.visit_definition.get_upper_window_datetime(
                    self.visit_instance.report_datetime),
                lab_entry=lab_entry,
                entry_status=entry_status,
            )
        return None

    @property
    def default_entry_status(self):
        return self.meta_data_instance.lab_entry.default_entry_status
