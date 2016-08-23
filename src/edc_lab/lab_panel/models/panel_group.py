from django.db import models

from edc_base.model.models import BaseModel


class PanelGroup (BaseModel):

    name = models.CharField(
        verbose_name="Panel Group Name",
        max_length=25,
        unique=True)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name, )

    class Meta:
        app_label = 'lab_panel'
        db_table = 'bhp_lab_core_panelgroup'
