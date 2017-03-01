from django.apps import apps as django_apps

from edc_label.label import Label

app_config = django_apps.get_app_config('edc_lab')
edc_protocol_app_config = django_apps.get_app_config('edc_protocol')


class BaseLabel(Label):

    model = django_apps.get_model(
        *app_config.aliquot_model.split('.'))
    requisition_model = django_apps.get_model(
        *app_config.requisition_model.split('.'))
    template_name = 'aliquot'

    def __init__(self, pk=None):
        super().__init__()
        self.object = self.model.objects.get(pk=pk)
