from django.urls import include, path
from django.views.generic import RedirectView
from edc_dashboard.views import AdministrationView
from edc_subject_dashboard.views import SubjectDashboardView
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

app_name = "edc_appointment"

urlpatterns = []

for app_name in [
    "edc_appointment",
    "edc_auth",
    "edc_device",
    "edc_protocol",
    "edc_reference",
    "edc_visit_schedule",
]:
    for p in paths_for_urlpatterns(app_name):
        urlpatterns.append(p)

urlpatterns.extend(
    SubjectDashboardView.urls(
        namespace=app_name,
        label="subject_dashboard",
        identifier_pattern=r"\w+",
    )
)


urlpatterns.extend(
    [
        path("administration/", AdministrationView.as_view(), name="administration_url"),
        path("i18n/", include("django.conf.urls.i18n")),
        path("", RedirectView.as_view(url="admin/"), name="home_url"),
        path("", RedirectView.as_view(url="admin/"), name="logout"),
    ]
)
