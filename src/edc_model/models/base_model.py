from django.db import models
from django_audit_fields.models import AuditModelMixin

from .url_model_mixin import UrlModelMixin


class BaseModel(UrlModelMixin, AuditModelMixin, models.Model):

    """Base model class for all EDC models. Adds created and modified'
    values for user, date and hostname (computer).
    """

    objects = models.Manager()

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    class Meta(AuditModelMixin.Meta):
        abstract = True
        default_permissions = ("add", "change", "delete", "view", "export", "import")
        default_manager_name = "objects"
