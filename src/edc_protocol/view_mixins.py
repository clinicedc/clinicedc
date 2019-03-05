from django.apps import apps as django_apps
from django.views.generic.base import ContextMixin


class EdcProtocolViewMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_config = django_apps.get_app_config("edc_protocol")
        context.update(
            {
                "protocol": app_config.protocol,
                "protocol_number": app_config.protocol_number,
                "protocol_name": app_config.protocol_name,
                "protocol_title": app_config.protocol_title,
            }
        )
        return context
