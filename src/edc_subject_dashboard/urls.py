from django.conf import settings
from django.contrib import admin
from django.urls.conf import path

from .views import RequisitionPrintActionsView, RequisitionVerifyActionsView

app_name = "edc_subject_dashboard"


urlpatterns = [
    path(
        r"requisition_print_actions/",
        RequisitionPrintActionsView.as_view(),
        name="requisition_print_actions_url",
    ),
    path(
        r"requisition_verify_actions/",
        RequisitionVerifyActionsView.as_view(),
        name="requisition_verify_actions_url",
    ),
]


if settings.APP_NAME == "edc_subject_dashboard":

    from edc_appointment.admin_site import edc_appointment_admin
    from edc_subject_dashboard.tests.admin import edc_subject_dashboard_admin

    urlpatterns += [
        path("admin/", admin.site.urls),
        path("admin/", edc_subject_dashboard_admin.urls),
        path("admin/", edc_appointment_admin.urls),
    ]
