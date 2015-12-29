from django.db import models

from lis.specimen.lab_panel.models import BasePanel

from ..choices import PANEL_TYPE

from .test_code import TestCode
from .aliquot_type import AliquotType


class Panel(BasePanel):

    edc_name = models.CharField(max_length=50, null=True)

    test_code = models.ManyToManyField(TestCode, null=True, blank=True)

    aliquot_type = models.ManyToManyField(AliquotType,
        help_text='Choose all that apply',)

    panel_type = models.CharField(max_length=15, choices=PANEL_TYPE, default='TEST')

    objects = models.Manager()

    def __unicode__(self):
        return self.edc_name or self.name

    def save(self, *args, **kwargs):
        if not self.edc_name:
            self.edc_name = self.name
        super(Panel, self).save(*args, **kwargs)

    class Meta:
        app_label = 'lab_clinic_api'
