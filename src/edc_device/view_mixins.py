from django.apps import apps as django_apps
from ipware.ip import get_ip, get_real_ip


class EdcDeviceViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config("edc_device")
        context.update(
            {
                "device_id": app_config.device_id,
                "device_role": app_config.device_role,
                "ip_address": self.ip_address,
            }
        )
        return context

    @property
    def ip_address(self):
        request = self.request
        try:
            ip_address = get_real_ip(request)
        except AttributeError:
            ip_address = None
        if not ip_address:
            try:
                ip_address = get_ip(request)
            except AttributeError:
                ip_address = None
        return ip_address
