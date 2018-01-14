from django.db import models

from .model_mixin import ModelMixin


class RequisitionMetadataModelMixin(ModelMixin):

    panel_name = models.CharField(max_length=50, null=True)

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

    class Meta(ModelMixin.Meta):
        abstract = True
        verbose_name = "Requisition Metadata"
        verbose_name_plural = "Requisition Metadata"
        unique_together = (('subject_identifier', 'visit_schedule_name',
                            'schedule_name', 'visit_code', 'visit_code_sequence',
                            'model', 'panel_name'), )
