from django.apps import apps as django_apps

from .base_label import BaseLabel


class ManifestLabel(BaseLabel):

    model = 'edc_lab.manifest'
    template_name = 'manifest'

    @property
    def label_context(self):
        edc_protocol_app_config = django_apps.get_app_config('edc_protocol')
        return {
            'barcode_value': self.model_obj.manifest_identifier,
            'manifest_identifier': self.model_obj.human_readable_identifier,
            'protocol': edc_protocol_app_config.protocol,
            'site': str(self.model_obj.site.id),
            'manifest_datetime': self.model_obj.manifest_datetime.strftime('%Y-%m-%d %H:%M'),
            'category': self.model_obj.get_category_display().upper(),
            'site_name': str(self.model_obj.site.name)}
