import re

from uuid import uuid4

from django.db import models

from edc_constants.constants import YES, UUID_PATTERN

from ...identifier import RequisitionIdentifier

human_readable_pattern = '^[0-9A-Z]{3}\-[0-9A-Z]{4}$'


class RequisitionIdentifierMixin(models.Model):

    requisition_identifier = models.CharField(
        verbose_name='Requisition Id',
        max_length=50,
        editable=False,
        unique=True)

    identifier_prefix = models.CharField(
        max_length=50,
        null=True,
        editable=False,
        unique=True)

    primary_aliquot_identifier = models.CharField(
        max_length=18,
        null=True,
        editable=False,
        unique=True)

    def save(self, *args, **kwargs):
        if not self.requisition_identifier:
            self.requisition_identifier = str(uuid4())
        self.requisition_identifier = self.get_requisition_identifier()
        super().save(*args, **kwargs)

    @property
    def human_requisition_identifier(self):
        """Returns a human readable requisition identifier.
        """
        x = self.requisition_identifier
        return '{}-{}'.format(x[0:3], x[3:7])

    def get_requisition_identifier(self):
        """Converts from uuid to a requisition identifier if
        is_drawn == YES and not already a requisition identifier.
        """
        is_uuid = re.match(UUID_PATTERN, self.requisition_identifier)
        if self.is_drawn == YES and is_uuid:
            return RequisitionIdentifier(self.__class__).identifier
        return self.requisition_identifier

    class Meta:
        abstract = True
