from django.apps import apps as django_apps
from edc_label import Label


class BaseLabel(Label):

    model_attr = None  # app_config attr such as aliquot_model, box_model, etc
    template_name = None
    requisition_model = None

    def __init__(self, pk=None, request=None, template_name=None, **kwargs):
        super().__init__(label_template_name=template_name or self.template_name)
        self.request = request
        app_config = django_apps.get_app_config('edc_lab')
        self.model_cls = django_apps.get_model(
            getattr(app_config, self.model_attr))
        self.requisition_model_cls = django_apps.get_model(
            self.requisition_model or app_config.requisition_model)
        self.model_obj = self.model_cls.objects.get(pk=pk)
        self.label_name = self.model_obj.human_readable_identifier
