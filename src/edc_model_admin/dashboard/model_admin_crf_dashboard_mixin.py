from edc_fieldsets import FieldsetsModelAdminMixin
from edc_visit_tracking.modeladmin_mixins import CrfModelAdminMixin

from .model_admin_subject_dashboard_mixin import ModelAdminSubjectDashboardMixin


class ModelAdminCrfDashboardMixin(
    FieldsetsModelAdminMixin, ModelAdminSubjectDashboardMixin, CrfModelAdminMixin,
):

    show_save_next = True
    show_cancel = True
    show_dashboard_in_list_display_pos = 1

    def get_subject_dashboard_url_kwargs(self, obj):
        return dict(
            subject_identifier=obj.subject_visit.subject_identifier,
            appointment=str(obj.subject_visit.appointment.id),
        )
