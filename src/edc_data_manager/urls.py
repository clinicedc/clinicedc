from django.conf import settings
from django.urls import path

from .admin_site import edc_data_manager_admin
from .views import HomeView

app_name = "edc_data_manager"

urlpatterns = [
    path("admin/", edc_data_manager_admin.urls),
    path("", HomeView.as_view(), name="home_url"),
]


if app_name == settings.APP_NAME:

    from django.urls import include
    from django.contrib import admin
    from edc_dashboard.views.administration_view import AdministrationView
    from edc_registration.admin_site import edc_registration_admin

    urlpatterns += [
        path("accounts/", include("edc_auth.urls")),
        path("admin/", include("edc_auth.urls")),
        path("admin/", edc_registration_admin.urls),
        path("admin/", admin.site.urls),
        path("edc_action_item/", include("edc_action_item.urls")),
        path("edc_protocol/", include("edc_protocol.urls")),
        path("edc_registration/", include("edc_registration.urls")),
        path("edc_dashboard/", include("edc_dashboard.urls")),
        path(
            "administration/", AdministrationView.as_view(), name="administration_url"
        ),
    ]
