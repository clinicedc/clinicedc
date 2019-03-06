import sys

from django.db import models
from django.conf import settings
from django_audit_fields.models import AuditUuidModelMixin


class Device(AuditUuidModelMixin, models.Model):
    pass


if settings.APP_NAME == "edc_device" and "makemigrations" not in sys.argv:
    from .tests.models import TestModel, TestModel2, TestModelPermissions  # noqa
