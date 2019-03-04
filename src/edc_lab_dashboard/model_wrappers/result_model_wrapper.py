from edc_lab.models import Result
from edc_model_wrapper import ModelWrapper

from ..dashboard_urls import dashboard_urls


class ResultModelWrapper(ModelWrapper):

    model_cls = Result
    next_url_name = dashboard_urls.get("result_listboard_url")
