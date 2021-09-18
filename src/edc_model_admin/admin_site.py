from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite as DjangoAdminSite
from django.contrib.sites.shortcuts import get_current_site
from edc_protocol import Protocol

admin.site.enable_nav_sidebar = False


class EdcAdminSite(DjangoAdminSite):

    """
    Add to your project urls.py
        path("edc_action_item/", edc_action_item.urls),

    -OR-
    To include this in the administration section set
    `AppConfig.include_in_administration_section = True`
    in your apps.py. (See also View `edc_dashboard.administration.py`).

    If set to `include_in_administration_section=True`, add a local `urls.py`

        from django.urls.conf import path
        from django.views.generic import RedirectView

        app_name = "edc_action_item"

        urlpatterns = [
            path("", RedirectView.as_view(url="admin/"), name="home_url"),
        ]

    and then add to your project urls.py

        path("edc_action_item/admin/", edc_action_item_admin.urls),
        path("edc_action_item/", include("edc_action_item.urls")),

    """

    app_index_template = "edc_model_admin/admin/app_index.html"
    login_template = f"edc_auth/bootstrap{settings.EDC_BOOTSTRAP}/login.html"
    logout_template = f"edc_auth/bootstrap{settings.EDC_BOOTSTRAP}/login.html"
    enable_nav_sidebar = False  # DJ 3.1
    final_catch_all_view = True  # DJ 3.2
    site_url = "/administration/"

    def __init__(self, name="admin", app_label=None, keep_delete_action=None):
        self.app_label = app_label
        super().__init__(name)
        if not keep_delete_action:
            del self._actions["delete_selected"]

    def each_context(self, request):
        context = super().each_context(request)
        context.update(global_site=get_current_site(request))
        context.update(
            site_title=self.get_edc_site_title(request),
            site_header=self.get_edc_site_header(request),
            index_title=self.index_title,
        )
        return context

    def get_edc_site_title(self, request):
        verbose_name = django_apps.get_app_config(self.app_label).verbose_name
        return verbose_name.replace(
            Protocol().project_name,
            f"{Protocol().project_name} @ {get_current_site(request).name.title()} ",
        )

    def get_edc_site_header(self, request):
        return self.get_edc_site_title(request)
