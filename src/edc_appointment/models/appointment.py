from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin

from ..managers import AppointmentManager
from ..model_mixins import AppointmentModelMixin


class Appointment(AppointmentModelMixin, SiteModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = AppointmentManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.subject_identifier,
                self.visit_schedule_name,
                self.schedule_name,
                self.visit_code,
                self.visit_code_sequence)
    natural_key.dependencies = ['sites.Site']

    class Meta(AppointmentModelMixin.Meta):
        pass
