from django.db import models
from django.utils import timezone

from edc_meta_data.managers import CrfMetaDataManager
from edc_testing.models import TestVisit


class DeathReport(models.Model):

    test_visit = models.OneToOneField(TestVisit)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date",
        default=timezone.now)

    entry_meta_data_manager = CrfMetaDataManager(TestVisit)

    class Meta:
        app_label = "edc_meta_data"
