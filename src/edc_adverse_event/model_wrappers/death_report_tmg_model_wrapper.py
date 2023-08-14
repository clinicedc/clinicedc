from edc_model_wrapper import ModelWrapper

from ..utils import get_adverse_event_app_label


class DeathReportTmgModelWrapper(ModelWrapper):
    next_url_name = "tmg_death_listboard_url"
    model = f"{get_adverse_event_app_label()}.deathreporttmg"
    next_url_attrs = ["subject_identifier"]

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def death_report(self):
        return str(self.object.death_report.id)
