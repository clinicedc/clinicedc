from math import floor

from django.apps import apps as django_apps
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic.base import ContextMixin

from edc_dashboard.utils import get_bootstrap_version


class AdministrationDashboardError(Exception):
    pass


class AdministrationViewMixin(ContextMixin):

    template_name = f"edc_dashboard/bootstrap{get_bootstrap_version()}/administration.html"

    edc_module_prefix = "Edc"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sections = self.sections
        context.update(sections=sections)
        index = 0
        col_one = {}
        col_two = {}
        col_three = {}
        per_col = floor(len(list(sections.keys())) / 3)
        for k, v in sections.items():
            index += 1
            if index <= per_col:
                col_one.update({k: v})
            elif index > per_col and index < (per_col * 2) + 1:
                col_two.update({k: v})
            else:
                col_three.update({k: v})
        context.update(col_one=col_one, col_two=col_two, col_three=col_three)
        return context

    def get_section(self, app_config=None):
        """Returns a dictionary for a single section.

        Format is {verbose_name: url_name}

        To be included must be a registered namespace. To main apps
        urls.py add paths. For example for `ambition_export`:

            urlpatterns = [
            ...
            path('admin/', ambition_export_admin.urls),
            path('ambition_export/', include('ambition_export.urls')),
            ...
            ]

        """
        section = {}
        try:
            url_namespace = app_config.url_namespace
        except AttributeError:
            url_namespace = app_config.name
        try:
            url = app_config.home_url_name
        except AttributeError:
            url = f"{url_namespace}:home_url"
        try:
            reverse(url)
        except NoReverseMatch as e:
            raise AdministrationDashboardError(
                f"Administrative section `{app_config.name}` url name is invalid. "
                f"Either fix the url name or set "
                f"`include_in_administration_section=False` in the AppConfig. "
                f"url_name=`{url}`. Got {e}"
            )
            # probably is not a registered namespace
            pass
        else:
            section = {app_config.verbose_name: url}
        return section

    @property
    def default_sections(self):
        return {
            "Accounts, Profiles, Logs": "edc_auth:home_url",
            # "Sites": "edc_sites_admin:home_url",
        }

    @property
    def sections(self):
        """Returns a dictionary (sorted) of the administration sections
        to show on the Administration page.
        """
        sections = {}
        for app_config in django_apps.get_app_configs():
            try:
                include = app_config.include_in_administration_section
            except AttributeError:
                include = False
            if include:
                sections.update(**self.get_section(app_config))
        sections.update(**self.default_sections)

        edc_sections = {
            k: v for k, v in sections.items() if k.startswith(self.edc_module_prefix)
        }
        edc_keys = list(edc_sections.keys())
        edc_keys.sort()

        other_sections = {
            k: v for k, v in sections.items() if not k.startswith(self.edc_module_prefix)
        }
        other_keys = list(other_sections.keys())
        other_keys.sort()

        keys = other_keys + edc_keys
        return {key: sections.get(key) for key in keys}
