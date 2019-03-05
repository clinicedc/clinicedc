from ..dashboard_urls import dashboard_urls
from .base_box_item_model_wrapper import BaseBoxItemModelWrapper


class ManageBoxItemModelWrapper(BaseBoxItemModelWrapper):

    action_name = "manage"
    next_url_name = dashboard_urls.get("manage_box_listboard_url")
