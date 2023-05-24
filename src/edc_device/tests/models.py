from django.db import models
from django_audit_fields.models import AuditUuidModelMixin
from edc_utils import get_utcnow


class TestModel(AuditUuidModelMixin, models.Model):
    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModel2(AuditUuidModelMixin, models.Model):
    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModelPermissions(AuditUuidModelMixin, models.Model):
    report_datetime = models.DateTimeField(default=get_utcnow)
