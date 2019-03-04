from django.apps import apps as django_apps

from ..dashboard_urls import dashboard_urls
from .base_box_item_model_wrapper import BaseBoxItemModelWrapper

app_config = django_apps.get_app_config("edc_lab_dashboard")


class VerifyBoxItemModelWrapper(BaseBoxItemModelWrapper):

    next_url_name = dashboard_urls.get("verify_box_listboard_url")
    action_name = "verify"
