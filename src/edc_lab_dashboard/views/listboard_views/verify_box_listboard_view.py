from copy import copy

from django.urls import reverse
from edc_dashboard.url_names import url_names
from edc_lab.constants import SHIPPED

from ...model_wrappers import VerifyBoxItemModelWrapper
from .base_box_item_listboard_view import BaseBoxItemListboardView


class VerifyBoxListboardView(BaseBoxItemListboardView):
    action_name = "verify"
    form_action_url = "verify_box_item_form_action_url"
    listboard_template = "verify_box_listboard_template"
    listboard_url = "verify_box_listboard_url"
    model_wrapper_cls = VerifyBoxItemModelWrapper
    navbar_selected_item = "pack"
    search_form_url = "verify_box_listboard_url"
    manage_box_listboard_url = "manage_box_listboard_url"
    verify_box_listboard_url = "verify_box_listboard_url"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            manage_box_listboard_url_reversed=self.manage_box_listboard_url_reversed,
            verify_box_listboard_url_reversed=self.verify_box_listboard_url_reversed,
            position=self.kwargs.get("position"),
            SHIPPED=SHIPPED,
        )
        return context

    @property
    def verify_box_listboard_url_reversed(self):
        url_kwargs = copy(self.url_kwargs)
        url_kwargs["position"] = 1
        url_kwargs["action_name"] = "verify"
        return reverse(url_names.get(self.verify_box_listboard_url), kwargs=url_kwargs)

    @property
    def manage_box_listboard_url_reversed(self):
        url_kwargs = copy(self.url_kwargs)
        url_kwargs.pop("position")
        url_kwargs["action_name"] = "manage"
        return reverse(url_names.get(self.manage_box_listboard_url), kwargs=url_kwargs)

    @property
    def url_kwargs(self):
        return {
            "action_name": self.action_name,
            "box_identifier": self.box_identifier,
            "position": self.kwargs.get("position", "1"),
        }
