from django.conf import settings
from edc_model_wrapper import ModelWrapper


class DeathReportTmgSecondModelWrapper(ModelWrapper):
    next_url_name = "tmg_death_listboard_url"
    model = f"{settings.ADVERSE_EVENT_APP_LABEL}.deathreporttmgsecond"
    next_url_attrs = ["subject_identifier"]

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def death_report(self):
        return str(self.object.death_report.id)
