from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from edc_fieldsets import FieldsetsModelAdminMixin
from edc_visit_tracking.modeladmin_mixins import CrfModelAdminMixin

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
            subject_identifier=obj.related_visit.subject_identifier,
            appointment=str(obj.related_visit.appointment.id),
        )

    def get_changeform_initial_data(self, request) -> dict:
        initial_data = super().get_changeform_initial_data(request)
        try:
            related_visit = self.related_visit(request)
        except ObjectDoesNotExist:
            report_datetime = None
        else:
            report_datetime = getattr(related_visit, self.report_datetime_field_attr, None)
        initial_data.update(report_datetime=report_datetime)
        return initial_data
