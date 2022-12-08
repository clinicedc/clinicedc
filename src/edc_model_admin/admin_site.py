from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite as DjangoAdminSite
from django.contrib.sites.shortcuts import get_current_site
from django.template.response import TemplateResponse
from edc_dashboard.utils import get_bootstrap_version
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

    index_template = "edc_model_admin/admin/index.html"
    app_index_template = "edc_model_admin/admin/app_index.html"
    login_template = f"edc_auth/bootstrap{get_bootstrap_version()}/login.html"
    logout_template = f"edc_auth/bootstrap{get_bootstrap_version()}/login.html"
    enable_nav_sidebar = False
    final_catch_all_view = True
    site_url = "/administration/"

    def __init__(
        self, name="admin", app_label=None, keep_delete_action=None, enable_nav_sidebar=None
    ):
        self.app_label = app_label
        if enable_nav_sidebar is not None:
            self.enable_nav_sidebar = enable_nav_sidebar
        super().__init__(name)
        if not keep_delete_action:
            del self._actions["delete_selected"]

    def each_context(self, request):
        context = super().each_context(request)
        context.update(
            site_title=self.get_edc_site_title(request),
            site_header=self.get_edc_site_header(request),
            global_site=get_current_site(request),
            protocol_name=Protocol().protocol_name,
            live_system=settings.LIVE_SYSTEM,
            DEBUG=settings.DEBUG,
        )
        return context

    def get_edc_site_title(self, request) -> str:
        verbose_name = django_apps.get_app_config(self.app_label).verbose_name
        return verbose_name.replace(
            Protocol().project_name,
            f"{Protocol().project_name} @ {get_current_site(request).name.title()} ",
        )

    def get_edc_site_header(self, request) -> str:
        return self.get_edc_site_title(request)

    def get_edc_index_title(self, request) -> str:
        return self.get_edc_site_title(request)

    def index(self, request, extra_context=None):
        app_list = self.get_app_list(request)
        context = {
            **self.each_context(request),
            "subtitle": None,
            "app_list": app_list,
            **(extra_context or {}),
        }
        request.current_app = self.name
        return TemplateResponse(request, self.index_template or "admin/index.html", context)
