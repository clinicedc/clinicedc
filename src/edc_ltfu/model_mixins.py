from django.core.validators import MinValueValidator
from django.db import models
from edc_constants.choices import YES_NO
from edc_model import models as edc_models
from edc_protocol.validators import date_not_before_study_start
from edc_utils.date import get_utcnow

from .choices import LOSS_CHOICES


class LossToFollowupModelMixin(models.Model):

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        validators=[date_not_before_study_start],
    )

    last_seen_datetime = models.DateField(
        verbose_name="Date participant last seen",
        validators=[date_not_before_study_start],
    )

    number_consecutive_missed_visits = models.IntegerField(
        verbose_name="Number of consecutive visits missed", null=True, blank=False
    )

    last_missed_visit_datetime = models.DateField(
        verbose_name="Date of last missed visit report submitted",
        null=True,
        blank=False,
    )

    ltfu_date = models.DateField(
        verbose_name="Date participant considered lost to follow up",
        default=get_utcnow,
        null=True,
        blank=False,
    )

    phone = models.CharField(
        verbose_name="Was contact by phone attempted",
        max_length=15,
        choices=YES_NO,
        null=True,
        blank=False,
    )
    phone_attempts = models.IntegerField(
        verbose_name=(
            "If YES, how many attempts were made to contact the participant by phone",
        ),
        validators=[MinValueValidator(0)],
        default=0,
    )

    home_visited = models.CharField(
        verbose_name="Was a home visit attempted", max_length=15, choices=YES_NO
    )

    home_visit_detail = models.TextField(
        verbose_name="If YES, provide any further details of the home visit",
        null=True,
        blank=True,
    )

    loss_category = models.CharField(
        verbose_name="Category of loss to follow up",
        max_length=25,
        choices=LOSS_CHOICES,
    )

    loss_category_other = edc_models.OtherCharField()

    comment = models.TextField(
        verbose_name=(
            "If any, please give additional details of the "
            "circumstances that led to this decision."
        ),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
        verbose_name = "Loss to Follow Up"
        verbose_name_plural = "Loss to Follow Ups"
