from django.db import models
from edc_base import get_utcnow
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin

from .locator_methods_model_mixin import LocatorMethodsModelMixin
from .subject_contact_fields_mixin import SubjectContactFieldsMixin
from .subject_indirect_contact_fields_mixin import SubjectIndirectContactFieldsMixin
from .subject_work_fields_mixin import SubjectWorkFieldsMixin


class LocatorManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class LocatorModelMixin(UniqueSubjectIdentifierFieldMixin,
                        SubjectContactFieldsMixin,
                        SubjectIndirectContactFieldsMixin,
                        SubjectWorkFieldsMixin,
                        LocatorMethodsModelMixin,
                        models.Model):

    """A model completed by the user to that captures participant
    locator information and permission to contact.
    """

    report_datetime = models.DateTimeField(default=get_utcnow)

    objects = LocatorManager()

    def __str__(self):
        return self.subject_identifier

    def natural_key(self):
        return (self.subject_identifier, )

    class Meta:
        abstract = True
