from django.urls.conf import path, re_path

from .admin_site import edc_visit_schedule_admin
from .views import HomeView, VisitScheduleView

app_name = "edc_visit_schedule"

urlpatterns = [
    path("admin/", edc_visit_schedule_admin.urls),
    re_path(
        r"visit_schedule/(?P<visit_schedule>[0-9A-Za-z_]+)/"
        "(?P<schedule>^[0-9A-Za-z_]+$)/(?P<visit_code>^[0-9]+$)/",
        VisitScheduleView.as_view(),
        name="visit_schedule_url",
    ),
    re_path(
        r"visit_schedule/(?P<visit_schedule>[0-9A-Za-z_]+)/(?P<schedule>^[0-9A-Za-z_]+$)/",
        VisitScheduleView.as_view(),
        name="visit_schedule_url",
    ),
    re_path(
        r"visit_schedule/(?P<visit_schedule>[0-9A-Za-z_]+)/",
        VisitScheduleView.as_view(),
        name="visit_schedule_url",
    ),
    re_path(
        r"visit_schedule/",
        VisitScheduleView.as_view(),
        name="visit_schedule_url",
    ),
    path(r"", HomeView.as_view(), name="home_url"),
]
