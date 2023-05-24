from django.db import models
from edc_model import models as edc_models


class PanelManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name, lab_profile_name):
        return self.get(name=name, lab_profile_name=lab_profile_name)


class Panel(edc_models.BaseUuidModel):
    name = models.CharField(max_length=50)

    display_name = models.CharField(max_length=50)

    lab_profile_name = models.CharField(max_length=50)

    objects = PanelManager()

    def __str__(self):
        return self.display_name or self.name

    def natural_key(self):
        return (self.name, self.lab_profile_name)

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Panel"
        unique_together = ("name", "lab_profile_name")
        ordering = ("lab_profile_name", "name")
