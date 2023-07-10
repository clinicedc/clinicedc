from django.conf import settings
from django.contrib import admin
from django.urls.conf import path
from edc_dashboard import url_names
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
        "refresh_subject_dashboard/<str:subject_visit_id>",
        RefreshMetadataActionsView.as_view(),
        name="refresh_metadata_actions_url",
    ),
    path(
        "refresh_appointments/<str:visit_schedule>/<str:schedule>/<str:subject_identifier>/",
        RefreshAppointmentsView.as_view(),
        name="refresh_appointments_url",
    ),
]

url_names.register(url="requisition_print_actions_url", namespace=app_name)
url_names.register(url="requisition_verify_actions_url", namespace=app_name)
url_names.register(url="refresh_metadata_actions_url", namespace=app_name)


if settings.APP_NAME == app_name:
    from edc_appointment.admin_site import edc_appointment_admin

    from edc_subject_dashboard.tests.admin import edc_subject_dashboard_admin

    urlpatterns += [
        path("admin/", admin.site.urls),
        path("admin/", edc_subject_dashboard_admin.urls),
        path("admin/", edc_appointment_admin.urls),
    ]
