from django.urls import include, path
from django.views.generic import RedirectView

from edc_dashboard.views import AdministrationView
from edc_subject_dashboard.views import SubjectDashboardView
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

app_name = "tests"

urlpatterns = [
    path("accounts/", include("edc_auth.urls")),
]

for app_name in [
    "tests",
    "edc_adverse_event",
    "edc_appointment",
    "edc_auth",
    "edc_dashboard",
    "edc_data_manager",
    "edc_device",
    "edc_device",
    "edc_export",
    "edc_lab",
    "edc_lab_dashboard",
    "edc_metadata",
    "edc_pharmacy",
    "edc_protocol",
    "edc_visit_schedule",
]:
    urlpatterns.extend(paths_for_urlpatterns(app_name))

urlpatterns.extend(
    SubjectDashboardView.urls(
        namespace=app_name,
        label="subject_dashboard",
        identifier_pattern=r"\w+",
    )
)

urlpatterns.extend(
    [
        path(
            "administration/", AdministrationView.as_view(), name="administration_url"
        ),
        path("i18n/", include("django.conf.urls.i18n")),
        path("", RedirectView.as_view(url="admin/"), name="home_url"),
        path("", RedirectView.as_view(url="admin/"), name="logout"),
    ]
)
