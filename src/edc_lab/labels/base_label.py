from django.apps import apps as django_apps

from edc_label.label import Label

app_config = django_apps.get_app_config('edc_lab')


class BaseLabel:

    label_cls = Label
    model_attr = None  # app_config attr such as aliquot_model, box_model, etc
    template_name = None

    def __init__(self, pk=None, **kwargs):
        super().__init__()
        app_config = django_apps.get_app_config('edc_lab')
        label_lower = getattr(app_config, self.model_attr)
        self.model = django_apps.get_model(label_lower)
        self.object = self.model.objects.get(pk=pk)
        self.label = self.label_cls(template_name=self.template_name)
        self.requisition_model = django_apps.get_model(
            app_config.requisition_model)

    @property
    def label_context(self):
        return {}

    @property
    def label_name(self):
        return self.object.human_readable_identifier

    def print_label(self):
        return self.label.print_label(copies=1, context=self.label_context)
