from django.urls.conf import path

from .admin_site import edc_visit_tracking_admin

app_name = "edc_visit_tracking"

urlpatterns = [path(r"admin/", edc_visit_tracking_admin.urls)]
