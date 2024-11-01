from django.db import models
from edc_list_data.model_mixins import ListModelMixin


class Manager(models.Manager):
    use_in_migrations = True


class Location(ListModelMixin):

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.capitalize()
        super().save(*args, **kwargs)

    class Meta(ListModelMixin.Meta):
        verbose_name = "Location"
        verbose_name_plural = "Locations"
