from django.db import models

from edc_base.model.models import BaseUuidModel
from edc_content_type_map.models import ContentTypeMap

from ..managers import AttachedModelManager
from .consent_catalogue import ConsentCatalogue


class AttachedModel(BaseUuidModel):
    """Models that are linked to a catalogue entry.

    Search the attached models by content_type_map to determine the
    consent_catalogue and from that, the edc_consent model."""
    consent_catalogue = models.ForeignKey(ConsentCatalogue)

    content_type_map = models.ForeignKey(
        ContentTypeMap,
        verbose_name='Subject model'
    )

    is_active = models.BooleanField(default=True)

    objects = AttachedModelManager()

    def natural_key(self):
        return self.consent_catalogue.natural_key() + self.content_type_map.natural_key()

    def __unicode__(self):
        return self.content_type_map.model

    class Meta:
        app_label = 'edc_consent'
        unique_together = (('consent_catalogue', 'content_type_map'), )
