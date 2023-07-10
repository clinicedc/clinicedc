from django.db import models

from edc_metadata.metadata_helper import MetadataHelperMixin


class MetadataHelperModelMixin(MetadataHelperMixin, models.Model):
    """The functionality here is mostly accessed in a signal.

    See edc_metadata/models/signals"""

    class Meta:
        abstract = True
