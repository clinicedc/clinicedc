from django.apps import apps as django_apps
from edc_device.constants import CLIENT, SERVER


class StudySiteNameQuerysetViewMixin:

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        app_config = django_apps.get_app_config('edc_lab')
        if app_config.site_name:
            edc_device_app_config = django_apps.get_app_config('edc_device')
            if edc_device_app_config.device_role in [SERVER, CLIENT]:
                options.update(site_name=app_config.study_site_name)
        return options
