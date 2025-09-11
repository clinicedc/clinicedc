from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.utils.html import format_html

from edc_constants.constants import YES

from ..listboard_filters import RequisitionListboardViewFilters
from .base_listboard_view import BaseListboardView


class RequisitionListboardView(BaseListboardView):
    listboard_model = settings.SUBJECT_REQUISITION_MODEL

    form_action_url = "requisition_form_action_url"
    listboard_template = "requisition_listboard_template"
    listboard_url = "requisition_listboard_url"
    listboard_view_filters = RequisitionListboardViewFilters()
    listboard_view_permission_codename = "edc_lab_dashboard.view_lab_requisition_listboard"
    listboard_view_only_my_permission_codename = None
    navbar_selected_item = "requisition"
    search_form_url = "requisition_listboard_url"
    show_all = True
    ordering = ["-modified", "-created"]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        unverified_requisition_count = (
            self.get_queryset().filter(clinic_verified__isnull=True).count()
        )
        if unverified_requisition_count:
            verb = "is" if unverified_requisition_count == 1 else "are"
            plural = "" if unverified_requisition_count == 1 else "s"
            messages.warning(
                self.request,
                format_html(
                    "There {} {} requisition{} "
                    "where the specimen is <b>drawn but not verified</b> by the clinic. "
                    "Please follow up.",
                    verb,
                    str(unverified_requisition_count),
                    plural,
                ),
            )
            kwargs.update(unverified_requisition_count=unverified_requisition_count)
        return super().get_context_data(**kwargs)

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        q_objects, options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(is_drawn=YES)
        return Q(), options
