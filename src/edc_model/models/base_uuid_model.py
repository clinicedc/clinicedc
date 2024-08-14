from django.db import models
from django_audit_fields.models import AuditUuidModelMixin

from .url_model_mixin import UrlModelMixin

default_permissions = ("add", "change", "delete", "view", "export", "import")


class BaseUuidModel(UrlModelMixin, AuditUuidModelMixin, models.Model):
    """Default manager must be `objects` for modelform validation to
    work correctly with unique fields.
    """

    objects = models.Manager()

    class Meta(AuditUuidModelMixin.Meta):
        abstract = True
        default_permissions = default_permissions
        default_manager_name = "objects"
        indexes = AuditUuidModelMixin.Meta.indexes
