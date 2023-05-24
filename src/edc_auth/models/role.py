from django.contrib.auth.models import Group
from django.db import models
from django.utils.text import slugify
from edc_model.models import BaseUuidModel


class RoleModelManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Role(BaseUuidModel):
    display_name = models.CharField(
        verbose_name="Display Name",
        max_length=250,
        unique=True,
        db_index=True,
        help_text="(suggest 40 characters max.)",
    )

    name = models.CharField(
        verbose_name="Name",
        max_length=250,
        unique=True,
        db_index=True,
        help_text="This is the stored value, required",
    )

    display_index = models.IntegerField(
        verbose_name="display index",
        default=0,
        db_index=True,
        help_text="Index to control display order if not alphabetical, not required",
    )

    objects = RoleModelManager()

    groups = models.ManyToManyField(Group)

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = slugify(self.display_name).lower()
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.name,)

    class Meta(BaseUuidModel.Meta):
        ordering = ["display_index", "display_name"]

        indexes = [models.Index(fields=["id", "display_name", "display_index"])]
