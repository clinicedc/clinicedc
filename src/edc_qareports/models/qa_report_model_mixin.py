from django.contrib.sites.models import Site
from django.db import models
from django.db.models import PROTECT

qa_reports_permissions = ("view", "export", "viewallsites")


class QaReportModelMixin(models.Model):

    report_model = models.CharField(max_length=50)

    subject_identifier = models.CharField(max_length=25)

    site = models.ForeignKey(Site, on_delete=PROTECT)

    created = models.DateTimeField()

    class Meta:
        abstract = True
        default_permissions = qa_reports_permissions
