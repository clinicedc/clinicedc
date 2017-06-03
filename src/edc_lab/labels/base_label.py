from django.apps import apps as django_apps

from edc_label.label import Label


class BaseLabel(Label):

    template_name = None
    model_attr = None  # app_config attr such as aliquot_model, box_model, etc

    def __init__(self, pk=None, **kwargs):
        super().__init__()
        app_config = django_apps.get_app_config('edc_lab')
        label_lower = getattr(app_config, self.model_attr)
        self.model = django_apps.get_model(*label_lower.split('.'))
        self.object = self.model.objects.get(pk=pk)

    @property
    def requisition_model(self):
        app_config = django_apps.get_app_config('edc_lab')
        return django_apps.get_model(
            *app_config.requisition_model.split('.'))
