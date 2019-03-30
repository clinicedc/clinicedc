from django.conf import settings
from django.contrib import messages
from edc_constants.constants import YES

from ...model_wrappers import RequisitionModelWrapper
from ..listboard_filters import RequisitionListboardViewFilters
from .base_listboard_view import BaseListboardView
from django.utils.safestring import mark_safe


class RequisitionListboardView(BaseListboardView):

    listboard_model = settings.SUBJECT_REQUISITION_MODEL

    form_action_url = "requisition_form_action_url"
    listboard_template = "requisition_listboard_template"
    listboard_url = "requisition_listboard_url"
    listboard_view_filters = RequisitionListboardViewFilters()
    listboard_view_permission_codename = "edc_dashboard.view_lab_requisition_listboard"
    listboard_view_only_my_permission_codename = None
    model_wrapper_cls = RequisitionModelWrapper
    navbar_selected_item = "requisition"
    search_form_url = "requisition_listboard_url"
    show_all = True
    ordering = ["-modified", "-created"]

    def __init__(self, **kwargs):
        self.unverified_requisition_count = 0
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.unverified_requisition_count:
            verb = "is" if self.unverified_requisition_count == 1 else "are"
            plural = "" if self.unverified_requisition_count == 1 else "s"
            messages.warning(
                self.request,
                mark_safe(
                    f"There {verb} {self.unverified_requisition_count} requisition{plural} "
                    "where the specimen is <b>drawn but not verified</b> by the clinic. "
                    "Please follow up."
                ),
            )
            context.update(
                unverified_requisition_count=self.unverified_requisition_count
            )
        return context

    def get_filtered_queryset(self, filter_options=None, exclude_options=None):
        queryset = super().get_filtered_queryset(filter_options, exclude_options)
        self.unverified_requisition_count = queryset.filter(
            clinic_verified__isnull=True
        ).count()
        return queryset

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options.update(is_drawn=YES)
        return options
