from datetime import date

from django_extensions.db.fields import UUIDField
from django.db import models

from edc_base.model.models import BaseModel


class SubjectIdentifierAuditTrail(BaseModel):
    """
    A table to track every attempt to allocate a subject identifier
    to a subject 'by this device'. If a subject's record is deleted
    the record in this table remains. So this is not a master list of
    valid identifiers.

    See also AllocateSubjectIdentifier()

    """
    subject_consent_id = UUIDField(auto=False)

    subject_identifier = models.CharField(
        max_length=25,
        unique=True)

    date_allocated = models.DateTimeField(
        default=date.today())

    def __unicode__(self):
        return '%s' % (self.subject_identifier)

    class Meta:
        ordering = ['-date_allocated']
        app_label = 'registration'
        db_table = 'bhp_registration_subjectidentifieraudittrail'
