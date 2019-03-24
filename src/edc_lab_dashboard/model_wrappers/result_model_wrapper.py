from edc_lab.models import Result
from edc_model_wrapper import ModelWrapper


class ResultModelWrapper(ModelWrapper):

    model_cls = Result
    next_url_name = "result_listboard_url"
