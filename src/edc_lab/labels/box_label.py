from django.apps import apps as django_apps

from .base_label import BaseLabel


class BoxLabel(BaseLabel):

    model_attr = 'box_model'
    template_name = 'box'

    @property
    def context(self):
        edc_protocol_app_config = django_apps.get_app_config('edc_protocol')
        return {
            'barcode_value': self.object.box_identifier,
            'box_identifier': self.object.human_readable_identifier,
            'protocol': edc_protocol_app_config.protocol,
            'site': edc_protocol_app_config.site_code,
            'box_datetime': self.object.box_datetime.strftime('%Y-%m-%d %H:%M'),
            'category': self.object.get_category_display().upper(),
            'specimen_types': self.object.specimen_types,
            'site_name': edc_protocol_app_config.site_name.upper()}
