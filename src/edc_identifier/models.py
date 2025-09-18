from django.db import models
from django.db.models import UniqueConstraint

from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin


class IdentifierModelManager(models.Manager):
    def get_by_natural_key(self, identifier):
        return self.get(identifier=identifier)

    @property
    def formatted_sequence(self):
        """Returns a padded sequence segment for the identifier"""
        if self.is_derived:
            return ""
        return str(self.sequence_number).rjust(self.padding, "0")

    class Meta:
        abstract = True


class IdentifierModel(SiteModelMixin, BaseUuidModel):
    identifier = models.CharField(max_length=50, unique=True)

    name = models.CharField(max_length=100)

    subject_identifier = models.CharField(max_length=50, default="")

    sequence_number = models.IntegerField(default=1)

    linked_identifier = models.CharField(max_length=50, default="")

    device_id = models.IntegerField()

    protocol_number = models.CharField(max_length=25, default="")

    model = models.CharField(max_length=100, default="")

    identifier_type = models.CharField(max_length=100, default="")

    identifier_prefix = models.CharField(max_length=25, default="")

    objects = IdentifierModelManager()

    def __str__(self):
        return f"{self.identifier} {self.name}"

    def natural_key(self):
        return (self.identifier,)

    class Meta(BaseUuidModel.Meta):
        app_label = "edc_identifier"
        constraints = (
            UniqueConstraint(
                fields=["name", "identifier"], name="%(app_label)s_%(class)s_name_uniq"
            ),
        )
        indexes = BaseUuidModel.Meta.indexes
