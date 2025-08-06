from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import edc_appointment_admin
from .views import UnscheduledAppointmentView

app_name = "edc_appointment"

urlpatterns = [
    path(
        "unscheduled_appointment/<subject_identifier>/<visit_schedule_name>"
        "/<schedule_name>/<visit_code>/<visit_code_sequence>/<timepoint>/<redirect_url>/",
        UnscheduledAppointmentView.as_view(),
        name="unscheduled_appointment_url",
    ),
    path("admin/", edc_appointment_admin.urls),
    path("", RedirectView.as_view(url="/edc_appointment/admin/"), name="home_url"),
]
