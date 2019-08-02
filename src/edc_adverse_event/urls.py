from django.urls.conf import path
from django.views.generic.base import RedirectView
from edc_adverse_event.admin_site import edc_adverse_event_admin

app_name = "edc_adverse_event"

urlpatterns = [
    path("admin/", edc_adverse_event_admin.urls),
    path("", RedirectView.as_view(url="/edc_adverse_event/admin/"), name="home_url"),
]
