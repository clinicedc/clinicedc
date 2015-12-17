from django.core.urlresolvers import reverse

from edc.core.bhp_common.utils import convert_from_camel
from edc_constants.constants import NOT_REQUIRED, ADDITIONAL, IN_PROGRESS
from edc.entry_meta_data.models import RequisitionMetaData
from edc.lab.lab_profile.classes import site_lab_profiles

from .base_scheduled_entry_context import BaseScheduledEntryContext


class RequisitionContext(BaseScheduledEntryContext):

    """A Class used by the dashboard when rendering the
    list of scheduled entries to display under "Scheduled Forms"."""

    meta_data_model = RequisitionMetaData

    def __init__(self, meta_data_instance, appointment, visit_model, requisition_model):
        self.requisition_model = requisition_model
        super(RequisitionContext, self).__init__(meta_data_instance, appointment, visit_model)

    def contribute_to_context(self, context):
        context.update({'label': self.meta_data_instance.lab_entry.requisition_panel.name,
                        'lab_entry': self.meta_data_instance.lab_entry})
        if self.instance:
            context.update({'requisition_identifier': self.instance.requisition_identifier})
        context.update({'panel': self.meta_data_instance.lab_entry.requisition_panel.pk})
        if site_lab_profiles.group_models.get('aliquot_type').objects.filter(
                alpha_code=self.meta_data_instance.lab_entry.requisition_panel.aliquot_type_alpha_code):
            alpha_code = self.meta_data_instance.lab_entry.requisition_panel.aliquot_type_alpha_code
            aliquot_type = site_lab_profiles.group_models.get(
                'aliquot_type').objects.get(alpha_code=alpha_code).pk
            context.update({'aliquot_type': aliquot_type})
        return context

    @property
    def model(self):
        return self.requisition_model

    @property
    def additional(self):
        return self.meta_data_instance.lab_entry.additional == ADDITIONAL

    @property
    def instance(self):
        """Sets to the model instance referred to by the requisition meta data."""
        if not self._instance:
            options = {
                convert_from_camel(self.visit_instance._meta.object_name): self.visit_instance,
                'panel': self.meta_data_instance.lab_entry.requisition_panel.pk}
            if self.model.objects.filter(**options):
                self._instance = self.model.objects.get(**options)
        return self._instance

    @property
    def model_url(self):
        """Returns the URL to the model referred to by the scheduled
        entry meta data if the current appointment is 'in progress'."""
        model_url = None
        if self.appointment.appt_status == IN_PROGRESS:
            if self.meta_data_instance.entry_status == NOT_REQUIRED:
                model_url = None
            elif not self.instance:
                model_url = reverse(
                    'admin:{app_label}_{model_name}_add'.format(
                        app_label=self.model._meta.app_label,
                        model_name=self.model._meta.object_name.lower()))
            elif self.instance:
                model_url = reverse(
                    'admin:{app_label}_{model_name}_change'.format(
                        app_label=self.model._meta.app_label,
                        model_name=self.model._meta.object_name.lower()), args=(self.instance.pk, ))
        return model_url
