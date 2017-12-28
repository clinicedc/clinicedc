from django.db import models
from edc_base import get_utcnow
from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin

from .subject_contact_fields_mixin import SubjectContactFieldsMixin
from .subject_indirect_contact_fields_mixin import SubjectIndirectContactFieldsMixin


class LocatorModelMixin(UniqueSubjectIdentifierFieldMixin,
                        SubjectContactFieldsMixin,
                        SubjectIndirectContactFieldsMixin,
                        models.Model):

    """A model completed by the user to that captures participant
    locator information and permission to contact.
    """

    report_datetime = models.DateTimeField(default=get_utcnow)

    objects = SubjectIdentifierManager()

    def __str__(self):
        return self.subject_identifier

    def natural_key(self):
        return (self.subject_identifier, )

    class Meta:
        abstract = True
