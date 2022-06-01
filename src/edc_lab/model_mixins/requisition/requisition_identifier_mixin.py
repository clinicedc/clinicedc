import re

from django.db import models
from edc_constants.constants import UUID_PATTERN, YES
from edc_protocol import Protocol
from edc_utils import get_uuid

from ...identifiers import RequisitionIdentifier

human_readable_pattern = r"^[0-9A-Z]{3}\-[0-9A-Z]{4}$"


class RequisitionIdentifierMixin(models.Model):
    requisition_identifier = models.CharField(
        verbose_name="Requisition Id", max_length=50, unique=True
    )

    identifier_prefix = models.CharField(max_length=50, null=True, editable=False, unique=True)

    primary_aliquot_identifier = models.CharField(
        max_length=18, null=True, editable=False, unique=True
    )

    def save(self, *args, **kwargs):
        if not self.requisition_identifier:
            self.requisition_identifier = get_uuid()
        self.protocol_number = self.get_protocol_number()
        self.requisition_identifier = self.get_requisition_identifier()
        super().save(*args, **kwargs)

    @property
    def human_readable_identifier(self):
        """Returns a human readable requisition identifier."""
        x = self.requisition_identifier
        return f"{x[0:3]}-{x[3:7]}"

    def get_protocol_number(self):
        """Returns the protocol number from the field or
        AppConfig.
        """
        protocol_number = self.protocol_number
        if not self.protocol_number:
            protocol_number = Protocol().protocol_number
        return protocol_number

    def get_requisition_identifier(self):
        """Converts from uuid to a requisition identifier if
        is_drawn == YES and not already a requisition identifier.
        """
        is_uuid = re.match(UUID_PATTERN, self.requisition_identifier)
        if (self.is_drawn == YES or not self.is_drawn) and is_uuid:
            return RequisitionIdentifier(
                protocol_number=self.protocol_number,
                subject_identifier=self.subject_identifier,
                source_model=self._meta.label_lower,
            ).identifier
        return self.requisition_identifier

    class Meta:
        abstract = True
