from django.db import models
from django.db.models import PROTECT
from edc_constants.choices import GENDER
from edc_model.models import BaseUuidModel
from edc_reportable import MICROMOLES_PER_LITER
from edc_screening.model_mixins import ScreeningIdentifierModelMixin
from edc_utils import get_utcnow

from edc_egfr.model_mixins import EgfrDropNotificationModelMixin


class SubjectScreening(ScreeningIdentifierModelMixin, BaseUuidModel):
    screening_identifier = models.CharField(
        verbose_name="Screening ID",
        max_length=50,
        blank=True,
        unique=True,
        editable=False,
    )

    gender = models.CharField(choices=GENDER, max_length=10)

    age_in_years = models.IntegerField()

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        help_text="Date and time of report.",
    )


class Appointment(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    appt_datetime = models.DateTimeField(
        verbose_name="Appointment date and time", db_index=True
    )

    class Meta(BaseUuidModel.Meta):
        pass


class SubjectVisit(BaseUuidModel):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=PROTECT,
    )

    subject_identifier = models.CharField(max_length=25, null=True)

    consent_version = models.CharField(max_length=5, default="1")

    report_datetime = models.DateTimeField()

    class Meta(BaseUuidModel.Meta):
        app_label = "egfr_app"


class EgfrDropNotification(EgfrDropNotificationModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)
    consent_version = models.CharField(max_length=5, default="1")

    class Meta(EgfrDropNotificationModelMixin.Meta, BaseUuidModel.Meta):
        app_label = "egfr_app"


class ResultCrf(models.Model):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date and Time",
        default=get_utcnow,
        help_text="Date and time of report.",
    )

    assay_datetime = models.DateTimeField(default=get_utcnow())

    egfr_value = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)

    egfr_units = models.CharField(
        verbose_name="units",
        max_length=10,
        choices=((MICROMOLES_PER_LITER, MICROMOLES_PER_LITER),),
        null=True,
        blank=True,
    )
