from django.contrib.sites.models import Site
from django.db import models
from django.db.models import DO_NOTHING, Index

from .qa_reports_permissions import qa_reports_permissions


class QaReportModelMixin(models.Model):

    report_model = models.CharField(max_length=50)

    subject_identifier = models.CharField(max_length=25)

    site = models.ForeignKey(Site, on_delete=DO_NOTHING)

    created = models.DateTimeField()

    class Meta:
        abstract = True
        default_permissions = qa_reports_permissions
        indexes = [Index(fields=["subject_identifier", "site"])]
