from django.apps import apps as django_apps

from .base_label import BaseLabel


edc_protocol_app_config = django_apps.get_app_config('edc_protocol')


class ManifestLabel(BaseLabel):

    model_attr = 'manifest_model'
    template_name = 'manifest'

    @property
    def label_context(self):
        return {
            'barcode_value': self.object.manifest_identifier,
            'manifest_identifier': self.object.human_readable_identifier,
            'protocol': edc_protocol_app_config.protocol,
            'site': edc_protocol_app_config.site_code,
            'manifest_datetime': self.object.manifest_datetime.strftime('%Y-%m-%d %H:%M'),
            'category': self.object.get_category_display().upper(),
            'site_name': edc_protocol_app_config.site_name.upper()}
