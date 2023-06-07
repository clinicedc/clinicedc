from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from ..managers import AppointmentManager
from ..model_mixins import AppointmentModelMixin
from .appointment_type import AppointmentType


class Appointment(AppointmentModelMixin, SiteModelMixin, BaseUuidModel):
    appt_type = models.ForeignKey(
        AppointmentType,
        verbose_name="Appointment type",
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=False,
        help_text="",
    )

    on_site = CurrentSiteManager()

    objects = AppointmentManager()

    history = HistoricalRecords()

    def natural_key(self) -> tuple:
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    # noinspection PyTypeHints
    natural_key.dependencies = ["sites.Site"]  # type: ignore

    def get_appt_type_display(self):
        return AppointmentType.objects.get(id=self.appt_type_id).display_name

    class Meta(AppointmentModelMixin.Meta, BaseUuidModel.Meta):
        pass
