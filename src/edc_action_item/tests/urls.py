from django.urls.conf import include, path
from edc_dashboard import url_names

from edc_action_item.admin_site import edc_action_item_admin

url_names.register("subject_dashboard_url", "subject_dashboard_url", "edc_action_item")


urlpatterns = [
    path("admin/", edc_action_item_admin.urls),
    path("", include("edc_action_item.urls")),
]
