from copy import copy
from django.urls.base import reverse
from edc_dashboard.url_names import url_names
from edc_lab.models import BoxItem

from ...model_wrappers import ManageBoxItemModelWrapper
from .base_box_item_listboard_view import BaseBoxItemListboardView


class ManageBoxListboardView(BaseBoxItemListboardView):

    action_name = "manage"
    form_action_url = "manage_box_item_form_action_url"
    listboard_url = "manage_box_listboard_url"
    listboard_template = "manage_box_listboard_template"
    verify_box_listboard_url = "verify_box_listboard_url"
    listboard_model = BoxItem
    model_wrapper_cls = ManageBoxItemModelWrapper
    navbar_selected_item = "pack"
    search_form_url = "manage_box_listboard_url"

    @property
    def url_kwargs(self):
        return {"action_name": self.action_name, "box_identifier": self.box_identifier}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_kwargs = copy(self.url_kwargs)
        url_kwargs["position"] = 1
        url_kwargs["action_name"] = "verify"
        context.update(
            verify_box_listboard_url_reversed=reverse(
                url_names.get(self.verify_box_listboard_url), kwargs=url_kwargs
            )
        )
        return context
