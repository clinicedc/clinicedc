from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from edc_constants.choices import GENDER, YES_NO, YES_NO_NA
from edc_constants.constants import NO, NOT_APPLICABLE
from edc_model.models.historical_records import HistoricalRecords
from edc_search.model_mixins import SearchSlugManager
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils.date import get_utcnow
from uuid import uuid4


class ScreeningManager(SearchSlugManager, models.Manager):

    use_in_migrations = True

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

    age_in_years = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(110)]
    )

    consent_ability = models.CharField(
        verbose_name="Participant or legal guardian/representative able and "
        "willing to give informed consent.",
        max_length=25,
        choices=YES_NO,
    )

    unsuitable_for_study = models.CharField(
        verbose_name=(
            "Is there any other reason the patient is "
            "deemed to not be suitable for the study?"
        ),
        max_length=5,
        choices=YES_NO,
        default=NO,
        help_text="If YES, patient NOT eligible, please give reason below.",
    )

    reasons_unsuitable = models.TextField(
        verbose_name="Reason not suitable for the study",
        max_length=150,
        null=True,
        blank=True,
    )

    unsuitable_agreed = models.CharField(
        verbose_name=(
            "Does the study coordinator agree that the patient "
            "is not suitable for the study?"
        ),
        max_length=5,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
    )

    eligible = models.BooleanField(default=False, editable=False)

    reasons_ineligible = models.TextField(
        verbose_name="Reason not eligible", max_length=150, null=True, editable=False
    )

    eligibility_datetime = models.DateTimeField(
        null=True, editable=False, help_text="Date and time eligibility was determined"
    )

    consented = models.BooleanField(default=False, editable=False)

    refused = models.BooleanField(default=False, editable=False)

    on_site = CurrentSiteManager()

    objects = ScreeningManager()

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
