from django.db import models

from edc_base.model.models import BaseUuidModel

from ..models import Panel


class PanelMapping(BaseUuidModel):

    panel_text = models.CharField(
        max_length=50,
        help_text='text name of external panel',
    )

    panel = models.ForeignKey(Panel, null=True, help_text="local panel definition")

    def __unicode__(self):
        return self.panel

    class Meta:
        app_label = "lab_clinic_api"
