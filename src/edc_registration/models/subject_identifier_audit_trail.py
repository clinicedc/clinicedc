from datetime import date
from uuid import uuid4

from django.db import models

from edc_base.model.models import BaseModel

try:
    from edc_sync.mixins import SyncMixin
except ImportError:
    SyncMixin = type('SyncMixin', (object, ), {})


class SubjectIdentifierAuditTrail(SyncMixin, BaseModel):
    """
    A table to track every attempt to allocate a subject identifier
    to a subject 'by this device'. If a subject's record is deleted
    the record in this table remains. So this is not a master list of
    valid identifiers.

    See also AllocateSubjectIdentifier()

    """
    subject_consent_id = models.UUIDField(
        default=uuid4
    )

    subject_identifier = models.CharField(
        max_length=25,
        unique=True)

    date_allocated = models.DateTimeField(
        default=date.today)

    def __unicode__(self):
        return '%s' % (self.subject_identifier)

    class Meta:
        app_label = 'edc_registration'
        ordering = ['-date_allocated']
