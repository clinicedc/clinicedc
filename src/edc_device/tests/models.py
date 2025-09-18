from django.db import models
from django.utils import timezone
from django_audit_fields.models import AuditUuidModelMixin


class TestModel(AuditUuidModelMixin, models.Model):
    report_datetime = models.DateTimeField(default=timezone.now)


class TestModel2(AuditUuidModelMixin, models.Model):
    report_datetime = models.DateTimeField(default=timezone.now)


class TestModelPermissions(AuditUuidModelMixin, models.Model):
    report_datetime = models.DateTimeField(default=timezone.now)
