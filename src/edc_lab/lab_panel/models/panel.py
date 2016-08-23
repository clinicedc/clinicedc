from django.db import models

from lis.specimen.lab_aliquot_list.models import AliquotType
from lis.specimen.lab_test_code.models import TestCode
from lis.subject.lab_account.models import Account

from .base_panel import BasePanel
from .panel_group import PanelGroup
from edc_lab.lab_panel.models.panel_model_mixin import PanelModelMixin


class Panel(PanelModelMixin):

    panel_group = models.ForeignKey(PanelGroup)

    test_code = models.ManyToManyField(
        TestCode,
        verbose_name='Test Codes',
        help_text='Choose all that apply')

    aliquot_type = models.ManyToManyField(
        AliquotType,
        help_text='Choose all that apply')

    account = models.ManyToManyField(
        Account,
        null=True,
        blank=True)

    dmis_panel_identifier = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name, )
    natural_key.dependencies = ['lab_panel.panel_group']

    class Meta:
        app_label = 'lab_panel'
        db_table = 'bhp_lab_core_panel'
        ordering = ['name', ]
