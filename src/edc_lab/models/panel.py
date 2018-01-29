from django.db import models
from edc_base.model_mixins import BaseUuidModel


class PanelManager(models.Manager):

    def get_by_natural_key(self, name, lab_profile_name):
        return self.get(name=name, lab_profile_name=lab_profile_name)


class Panel(BaseUuidModel):

    name = models.CharField(
        max_length=50)

    display_name = models.CharField(
        max_length=50)

    lab_profile_name = models.CharField(
        max_length=50)

    objects = PanelManager()

    def __str__(self):
        return self.display_name or self.name

    def natural_key(self):
        return (self.name, self.lab_profile_name)

    class Meta:
        unique_together = ('name', 'lab_profile_name')
        ordering = ('lab_profile_name', 'name')
