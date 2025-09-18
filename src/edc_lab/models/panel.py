from django.db import models
from django.db.models import UniqueConstraint

from edc_model.models import BaseUuidModel


class PanelManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name, lab_profile_name):
        return self.get(name=name, lab_profile_name=lab_profile_name)


class Panel(BaseUuidModel):
    name = models.CharField(max_length=50)

    display_name = models.CharField(max_length=50)

    lab_profile_name = models.CharField(max_length=50)

    objects = PanelManager()

    def __str__(self):
        return self.display_name or self.name

    def natural_key(self):
        return self.name, self.lab_profile_name

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Panel"
        verbose_name_plural = "Panels"
        constraints = (
            UniqueConstraint(
                fields=["name", "lab_profile_name"],
                name="%(app_label)s_%(class)s_name_uniq",
            ),
        )
