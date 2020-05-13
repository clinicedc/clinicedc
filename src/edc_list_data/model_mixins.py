from django.db import models
from django.utils.text import slugify


class ListModelManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ListModelMixin(models.Model):

    """Mixin for list data used in dropdown and radio widgets having
    display value and store value pairs.
    """

    # FIXME: this should be a short string, e.g. 15-25 chars!
    name = models.CharField(
        verbose_name="Stored value",
        max_length=250,
        unique=True,
        db_index=True,
        help_text="This is the stored value, required",
    )

    display_name = models.CharField(
        verbose_name="Name",
        max_length=250,
        unique=True,
        db_index=True,
        help_text="(suggest 40 characters max.)",
    )

    display_index = models.IntegerField(
        verbose_name="display index",
        default=0,
        db_index=True,
        help_text=("Index to control display order if not alphabetical, not required"),
    )

    field_name = models.CharField(
        max_length=25, editable=False, null=True, blank=True, help_text="Not required"
    )

    version = models.CharField(max_length=35, editable=False, default="1.0")
    objects = ListModelManager()

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = slugify(self.display_name).lower()
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.name,)

    class Meta:
        abstract = True
        ordering = ["display_index", "display_name"]
        indexes = [models.Index(fields=["id", "display_name", "display_index"])]
        default_permissions = ("add", "change", "delete", "view", "export", "import")
