from django.db import models

from edc_metadata.metadata_helper import MetadataHelperMixin


class MetadataHelperModelMixin(MetadataHelperMixin, models.Model):
    class Meta:
        abstract = True
