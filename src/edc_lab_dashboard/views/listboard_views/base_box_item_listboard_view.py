from __future__ import annotations

from typing import TYPE_CHECKING

from ...view_mixins import BoxViewMixin
from .base_listboard_view import BaseListboardView

if TYPE_CHECKING:
    from django.db.models import Q


class BaseBoxItemListboardView(BoxViewMixin, BaseListboardView):
    navbar_selected_item = "pack"
    ordering = ("-position",)
    listboard_model = "edc_lab.boxitem"
    listboard_view_permission_codename = "edc_lab_dashboard.view_lab_box_listboard"

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_object, options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update({"box": self.box})
        return q_object, {"box": self.box}
