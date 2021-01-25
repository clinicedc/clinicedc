from django.contrib.admin import AdminSite as DjangoAdminSite
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import admin

admin.site.enable_nav_sidebar = False


class EdcAdminSite(DjangoAdminSite):
    def __init__(self, name="admin"):
        super().__init__(name)
        del self._actions["delete_selected"]

    def each_context(self, request):
        context = super().each_context(request)
        context.update(global_site=get_current_site(request))
        return context

    """
    To inlcude this in the administration section set
    `AppConfig.include_in_administration_section = True`
    in your apps.py. (See also View `edc_dashboard.administration.py`).

    Add to your project urls.py
        path("admin/", edc_action_item.urls),

    if set to include_in_administration_section=True, add a local `urls.py`

        from django.urls import path
        from django.views.generic.base import RedirectView

        from .admin_site import edc_action_item_admin

        app_name = "edc_action_item"

        urlpatterns = [
            path("admin/", edc_action_item.urls),
            path("", RedirectView.as_view(url=f"/{app_name}/admin/"), name="home_url"),
        ]

    and then add to your project urls.py

        path("edc_action_item/", include("edc_action_item.urls")),

    """

    site_url = "/administration/"
    enable_nav_sidebar = False  # DJ 3.1
