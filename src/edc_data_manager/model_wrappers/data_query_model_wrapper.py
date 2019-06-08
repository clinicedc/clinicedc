from edc_model_wrapper import ModelWrapper

from ..models import DataQuery


class DataQueryModelWrapper(ModelWrapper):

    model_cls = DataQuery
    next_url_attrs = ["subject_identifier"]
    next_url_name = "subject_dashboard_url"

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def str_pk(self):
        return str(self.object.id)
