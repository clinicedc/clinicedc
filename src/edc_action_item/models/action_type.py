from django.db import models
from django.utils.safestring import mark_safe
from edc_base.model_mixins import BaseUuidModel

from ..choices import PRIORITY
from ..constants import HIGH_PRIORITY


class ActionType(BaseUuidModel):

    name = models.CharField(
        max_length=50,
        unique=True)

    display_name = models.CharField(
        max_length=100,
        unique=True)

    prn_form_action = models.BooleanField(
        verbose_name='Action requires a PRN form to be completed?',
        help_text='If True, specify model.')

    model = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    priority = models.CharField(
        max_length=25,
        choices=PRIORITY,
        default=HIGH_PRIORITY)

    show_on_dashboard = models.BooleanField(
        default=True)

    instructions = models.TextField(
        max_length=250,
        null=True,
        blank=True)

    def __str__(self):
        return self.name

    @property
    def prn(self):
        return mark_safe(self.prn_form_action)

    def save(self, *args, **kwargs):
        self.display_name = self.display_name or self.name
        super().save(*args, **kwargs)
