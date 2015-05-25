from django.db import models
from edc.audit.audit_trail import AuditTrail
from edc.base.model.models import BaseUuidModel
from edc.core.bhp_content_type_map.models import ContentTypeMap
from edc_consent import AttachedModelManager
from edc_consent_catalogue import ConsentCatalogue


class AttachedModel(BaseUuidModel):
    """Models that are linked to a catalogue entry.

    Search the attached models by content_type_map to determine the consent_catalogue and from that, the edc_consent model."""
    consent_catalogue = models.ForeignKey(ConsentCatalogue)

    # the content type map of a subject model
    content_type_map = models.ForeignKey(
        ContentTypeMap,
        verbose_name='Subject model'
    )

    is_active = models.BooleanField(default=True)

    history = AuditTrail()

    objects = AttachedModelManager()

    def natural_key(self):
        return self.consent_catalogue.natural_key() + self.content_type_map.natural_key()

    def __unicode__(self):
        return self.content_type_map.model

    class Meta:
        app_label = 'edc_consent'
        db_table = 'bhp_consent_attachedmodel'  # TODO: refactor SQL schema to remove
        unique_together = (('consent_catalogue', 'content_type_map'), )
