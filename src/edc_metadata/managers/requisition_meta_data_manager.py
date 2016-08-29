from django.core.exceptions import ImproperlyConfigured

from ..models import RequisitionMetaData, LabEntry

from .base_meta_data_manager import BaseMetaDataManager


class RequisitionMetaDataManager(BaseMetaDataManager):

    meta_data_model = RequisitionMetaData
    entry_model = LabEntry
    entry_attr = 'lab_entry'

    def __init__(self, visit_model, visit_attr_name=None):
        self._target_requisition_panel = None
        super(RequisitionMetaDataManager, self).__init__(visit_model, visit_attr_name)

    def __repr__(self):
        return 'RequisitionMetaDataManager({0.instance!r})'.format(self)

    def __str__(self):
        return '({0.instance!s})'.format(self)

    @property
    def target_requisition_panel(self):
        return self._target_requisition_panel

    @target_requisition_panel.setter
    def target_requisition_panel(self, target_requisition_panel):
        self._target_requisition_panel = target_requisition_panel
        self._meta_data_instance = None

    @property
    def query_options(self):
        return {self.visit_attr_name: self.visit_instance, 'panel__name': self.target_requisition_panel.lower() if isinstance(self.target_requisition_panel, str) else self.target_requisition_panel.name.lower()}

    @property
    def meta_data_query_options(self):
        """Returns the options used to query the meta data model for the meta_data_instance."""
        return {'appointment': self.visit_instance.appointment,
                '{0}__app_label'.format(self.entry_attr): self.model._meta.app_label,
                '{0}__model_name'.format(self.entry_attr): self.model._meta.object_name.lower(),
                '{0}__requisition_panel__name__iexact'.format(self.entry_attr): self.target_requisition_panel.lower() if isinstance(self.target_requisition_panel, str) else self.target_requisition_panel.name.lower()}

    def create_meta_data(self):
        """Creates a meta_data instance for the model at the
        time point (appointment) for the given registered_subject.

        might return None and meta data not created based on visit reason (e.g. missed)."""
        lab_entry = None
        if self.visit_instance.reason not in self.skip_create_visit_reasons:
            try:
                lab_entry = self.entry_model.objects.get(
                    app_label=self.model._meta.app_label.lower(),
                    model_name=self.model._meta.object_name.lower(),
                    visit_definition__code=self.visit_instance.appointment.visit_definition.code,
                    requisition_panel__name__iexact=self.target_requisition_panel.lower() if isinstance(self.target_requisition_panel, str) else self.target_requisition_panel.name.lower(),
                )
            except self.entry_model.DoesNotExist:
                pass
                #raise ImproperlyConfigured('LabEntry matching query does not exist. Model {0}.Check your'
                #                           ' visit schedule configuration or rule groups.'.format(self.model))
            if self.visit_instance.appointment.visit_instance != '0':
                entry_status = 'NOT_REQUIRED'
            else:
                entry_status = lab_entry.default_entry_status if lab_entry else None
            if lab_entry:
                return self.meta_data_model.objects.create(
                    appointment=self.visit_instance.appointment,
                    registered_subject=self.visit_instance.appointment.registered_subject,
                    due_datetime=lab_entry.visit_definition.get_upper_window_datetime(
                        self.visit_instance.report_datetime),
                    lab_entry=lab_entry,
                    entry_status=entry_status,
                )
            return None
        return None

    @property
    def default_entry_status(self):
        return self.meta_data_instance.lab_entry.default_entry_status
