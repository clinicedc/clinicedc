from django.urls.conf import path

from edc_dashboard.url_names import url_names
from edc_metadata.views import RefreshMetadataActionsView

from .views import (
    RefreshAppointmentsView,
    RequisitionPrintActionsView,
    RequisitionVerifyActionsView,
)

app_name = "edc_subject_dashboard"


urlpatterns = [
    path(
        "requisition_print_actions/",
        RequisitionPrintActionsView.as_view(),
        name="requisition_print_actions_url",
    ),
    path(
        "requisition_verify_actions/",
        RequisitionVerifyActionsView.as_view(),
        name="requisition_verify_actions_url",
    ),
    path(
        "refresh_subject_dashboard/<str:visit_schedule_name>/<str:schedule_name>"
        "/<str:related_visit_id>/",
        RefreshMetadataActionsView.as_view(),
        name="refresh_metadata_actions_url",
    ),
    path(
        "refresh_appointments/<str:visit_schedule_name>/<str:schedule_name>/"
        "<str:subject_identifier>/",
        RefreshAppointmentsView.as_view(),
        name="refresh_appointments_url",
    ),
]

url_names.register(url="requisition_print_actions_url", namespace=app_name)
url_names.register(url="requisition_verify_actions_url", namespace=app_name)
url_names.register(url="refresh_metadata_actions_url", namespace=app_name)
