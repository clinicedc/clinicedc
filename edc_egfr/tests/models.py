from django.db import models
from django.db.models import PROTECT
from edc_appointment.models import Appointment
from edc_constants.choices import GENDER
from edc_model.models import BaseUuidModel
from edc_screening.model_mixins import ScreeningIdentifierModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_tracking.model_mixins import VisitModelMixin

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


class SubjectVisit(
    VisitModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=PROTECT,
    )

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()

    reason = models.CharField(max_length=25, null=True)

    class Meta(BaseUuidModel.Meta):
        pass


class EgfrDropNotification(EgfrDropNotificationModelMixin, BaseUuidModel):
    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    class Meta(EgfrDropNotificationModelMixin.Meta, BaseUuidModel.Meta):
        app_label = "edc_egfr"
