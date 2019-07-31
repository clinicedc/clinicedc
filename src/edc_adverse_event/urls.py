from django.urls.conf import path

from edc_adverse_event.admin_site import edc_adverse_event_admin

app_name = "ambition_ae"

urlpatterns = [path("admin/", edc_adverse_event_admin.urls)]
