from django.apps import apps as django_apps

from .base_label import BaseLabel, app_config, edc_protocol_app_config


class ManifestLabel(BaseLabel):

    model = django_apps.get_model(*app_config.manifest_model.split('.'))
    template_name = 'manifest'

    @property
    def context(self):
        return {
            'barcode_value': self.object.manifest_identifier,
            'manifest_identifier': self.object.human_readable_identifier,
            'protocol': edc_protocol_app_config.protocol,
            'site': edc_protocol_app_config.site_code,
            'manifest_datetime': self.object.manifest_datetime.strftime('%Y-%m-%d %H:%M'),
            'category': self.object.get_category_display().upper(),
            'site_name': edc_protocol_app_config.site_name.upper()}
