from django.conf import settings
from django.contrib import admin
from django.urls.conf import path
from edc_dashboard import url_names

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

url_names.register(url="requisition_print_actions_url", namespace=app_name)
url_names.register(url="requisition_verify_actions_url", namespace=app_name)


if settings.APP_NAME == app_name:

    from edc_appointment.admin_site import edc_appointment_admin
    from edc_subject_dashboard.tests.admin import edc_subject_dashboard_admin

    urlpatterns += [
        path("admin/", admin.site.urls),
        path("admin/", edc_subject_dashboard_admin.urls),
        path("admin/", edc_appointment_admin.urls),
    ]
