import uuid

from django.db import models
from django.utils import timezone

from ..constants import DELETE, INSERT, UPDATE


class ExportTrackingFieldsModelMixin(models.Model):

    """Adds these fields to the Concrete model."""

    exported = models.BooleanField(
        default=False,
        editable=False,
        help_text=(
            "system field for export tracking. considered "
            "'exported' if both sent and received."
        ),
    )

    exported_datetime = models.DateTimeField(
        null=True, editable=False, help_text="system field for export tracking."
    )

    export_change_type = models.CharField(
        max_length=1,
        choices=((INSERT, "Insert"), (UPDATE, "Update"), (DELETE, "Delete")),
        default=INSERT,
        editable=False,
        help_text="system field for export tracking.",
    )

    export_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="system field for export tracking.",
    )

    def update_export_mixin_fields(self):
        self.exported = True
        self.exported_datetime = timezone.now()
        self.save()

    class Meta:
        abstract = True
