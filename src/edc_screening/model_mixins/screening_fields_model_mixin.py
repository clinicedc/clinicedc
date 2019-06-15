from django.db import models
from edc_constants.choices import GENDER
from edc_model.models.historical_records import HistoricalRecords
from edc_search.model_mixins import SearchSlugManager
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils.date import get_utcnow
from uuid import uuid4


class ScreeningManager(SearchSlugManager, models.Manager):
    def get_by_natural_key(self, screening_identifier):
        return self.get(screening_identifier=screening_identifier)


class ScreeningFieldsModeMixin(SiteModelMixin, models.Model):
    reference = models.UUIDField(
        verbose_name="Reference", unique=True, default=uuid4, editable=False
    )

    screening_identifier = models.CharField(
        verbose_name="Screening ID",
        max_length=50,
        blank=True,
        unique=True,
        editable=False,
    )

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        help_text="Date and time of report.",
    )

    gender = models.CharField(choices=GENDER, max_length=10)

    age_in_years = models.IntegerField()

    eligible = models.BooleanField(default=False, editable=False)

    reasons_ineligible = models.TextField(
        verbose_name="Reason not eligible", max_length=150, null=True, editable=False
    )

    consented = models.BooleanField(default=False, editable=False)

    on_site = CurrentSiteManager()

    objects = ScreeningManager()

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
