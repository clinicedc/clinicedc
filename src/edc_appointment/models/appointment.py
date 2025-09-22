from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin

from ..managers import AppointmentManager
from ..model_mixins import AppointmentModelMixin


class Appointment(AppointmentModelMixin, SiteModelMixin, BaseUuidModel):
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
    natural_key.dependencies = ("sites.Site",)

    class Meta(AppointmentModelMixin.Meta, SiteModelMixin.Meta, BaseUuidModel.Meta):
        indexes = (*AppointmentModelMixin.Meta.indexes, *BaseUuidModel.Meta.indexes)
