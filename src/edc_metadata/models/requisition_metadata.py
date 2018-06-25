from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin

from .managers import RequisitionMetadataManager
from .model_mixin import ModelMixin


class RequisitionMetadata(ModelMixin, SiteModelMixin, BaseUuidModel):

    panel_name = models.CharField(max_length=50, null=True)

    on_site = CurrentSiteManager()

    objects = RequisitionMetadataManager()

    def __str__(self):
        return (f'RequisitionMeta {self.model}.{self.visit_code}.'
                f'{self.visit_code_sequence} {self.panel_name} '
                f'{self.entry_status} {self.subject_identifier}')

    @property
    def verbose_name(self):
        return self.panel_name

    def natural_key(self):
        return (self.panel_name, self.model, self.subject_identifier,
                self.visit_schedule_name, self.schedule_name, self.visit_code,
                self.visit_code_sequence)
    natural_key.dependencies = ['sites.Site']

    class Meta:
        app_label = 'edc_metadata'
        verbose_name = "Requisition Metadata"
        verbose_name_plural = "Requisition Metadata"
        unique_together = (('subject_identifier', 'visit_schedule_name',
                            'schedule_name', 'visit_code', 'visit_code_sequence',
                            'model', 'panel_name'), )
