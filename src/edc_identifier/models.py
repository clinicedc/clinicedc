from django.db import models
from edc_model import models as edc_models
from edc_sites.models import SiteModelMixin


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


class IdentifierModel(SiteModelMixin, edc_models.BaseUuidModel):
    name = models.CharField(max_length=100)

    subject_identifier = models.CharField(max_length=50, null=True)

    sequence_number = models.IntegerField(default=1)

    identifier = models.CharField(max_length=50, unique=True)

    linked_identifier = models.CharField(max_length=50, null=True)

    device_id = models.IntegerField()

    protocol_number = models.CharField(max_length=25, null=True)

    model = models.CharField(max_length=100, null=True)

    identifier_type = models.CharField(max_length=100, null=True)

    identifier_prefix = models.CharField(max_length=25, null=True)

    objects = IdentifierModelManager()

    def __str__(self):
        return f"{self.identifier} {self.name}"

    def natural_key(self):
        return (self.identifier,)

    class Meta(edc_models.BaseUuidModel.Meta):
        app_label = "edc_identifier"
        ordering = ["sequence_number"]
        unique_together = ("name", "identifier")
