from django.db import models
from django.utils.text import slugify

from edc_model.models import BaseUuidModel


class ListModelManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class BaseListModelMixin(models.Model):
    # FIXME: this should be a short string, e.g. 15-25 chars!
    name = models.CharField(
        verbose_name="Stored value",
        max_length=250,
        unique=True,
        help_text="This is the stored value, required",
    )

    plural_name = models.CharField(
        verbose_name="Plural name",
        max_length=250,
        default="",
    )

    display_name = models.CharField(
        verbose_name="Name",
        max_length=250,
        unique=True,
        help_text="(suggest 40 characters max.)",
    )

    display_index = models.IntegerField(
        verbose_name="display index",
        default=0,
        help_text="Index to control display order if not alphabetical, not required",
    )

    field_name = models.CharField(
        max_length=25,
        editable=False,
        default="",
        blank=True,
        help_text="Not required",
    )

    extra_value = models.CharField(max_length=250, default="")

    version = models.CharField(max_length=35, editable=False, default="1.0")

    objects = ListModelManager()

    def __str__(self) -> str:
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = slugify(self.display_name).lower()
        if not self.plural_name:
            self.plural_name = f"{self.name}s"
        super().save(*args, **kwargs)

    def natural_key(self) -> tuple:
        return (self.name,)

    class Meta:
        abstract = True
        indexes = (models.Index(fields=["display_index", "display_name"]),)
        default_permissions = ("add", "change", "delete", "view", "export", "import")


class ListModelMixin(BaseListModelMixin):
    """Mixin for list data used in dropdown and radio widgets having
    display value and store value pairs.
    """

    id = models.AutoField(primary_key=True)

    class Meta(BaseListModelMixin.Meta):
        abstract = True
        indexes = BaseListModelMixin.Meta.indexes


class ListModelMixin2(BaseListModelMixin):
    """Mixin for list data used in dropdown and radio widgets having
    display value and store value pairs.

    Includes field "custom_name"
    """

    id = models.AutoField(primary_key=True)

    custom_name = models.CharField(
        max_length=25,
        default="",
        blank=True,
        help_text="A custom name/value to use on export instead of or in addition to `name`",
    )

    class Meta(BaseListModelMixin.Meta):
        abstract = True
        indexes = BaseListModelMixin.Meta.indexes


class ListUuidModelMixin(BaseListModelMixin, BaseUuidModel):
    """Mixin with UUID pk for list data used in dropdown
    and radio widgets having display value and store value pairs.
    """

    class Meta(BaseListModelMixin.Meta, BaseUuidModel.Meta):
        abstract = True
        indexes = (*BaseListModelMixin.Meta.indexes, *BaseUuidModel.Meta.indexes)
