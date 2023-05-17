from django.apps import apps as django_apps
from edc_label import Label


class BaseLabel(Label):
    model = None  # lower_label
    template_name = None

    def __init__(self, pk=None, request=None, template_name=None, **kwargs):
        super().__init__(label_template_name=template_name or self.template_name)
        self.request = request
        self.model_cls = django_apps.get_model(self.model)
        self.model_obj = self.model_cls.objects.get(pk=pk)
        self.label_name = self.model_obj.human_readable_identifier
