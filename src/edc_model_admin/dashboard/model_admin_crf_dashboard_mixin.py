from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from edc_fieldsets import FieldsetsModelAdminMixin
from edc_visit_tracking.modeladmin_mixins import CrfModelAdminMixin
from edc_visit_tracking.utils import get_subject_visit_model_cls

from .model_admin_subject_dashboard_mixin import ModelAdminSubjectDashboardMixin


class ModelAdminCrfDashboardMixin(
    FieldsetsModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    CrfModelAdminMixin,
):

    show_save_next = True
    show_cancel = True
    show_dashboard_in_list_display_pos = 1

    def get_subject_dashboard_url_kwargs(self, obj) -> dict:
        return dict(
            subject_identifier=obj.subject_visit.subject_identifier,
            appointment=str(obj.subject_visit.appointment.id),
        )

    def get_changeform_initial_data(self: Any, request) -> dict:
        initial_data = super().get_changeform_initial_data(request)  # noqa
        try:
            subject_visit = get_subject_visit_model_cls().objects.get(
                id=request.GET.get(self.model.visit_model_attr())
            )
        except ObjectDoesNotExist:
            # TODO: how do we get here? PRN?
            pass
        else:
            initial_data.update(
                report_datetime=subject_visit.report_datetime,
            )
        return initial_data
