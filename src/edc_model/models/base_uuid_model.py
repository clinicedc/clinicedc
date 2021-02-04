from django.db import models
from django_audit_fields.models import AuditUuidModelMixin

from .url_model_mixin import UrlModelMixin


class BaseUuidModel(UrlModelMixin, AuditUuidModelMixin, models.Model):

    objects = models.Manager()

    class Meta(AuditUuidModelMixin.Meta):
        abstract = True
        default_permissions = ("add", "change", "delete", "view", "export", "import")
