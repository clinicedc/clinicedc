from django.apps import apps as django_apps


class RequisitionModelViewMixin:

    @property
    def requisition_model(self):
        edc_lab_app_config = django_apps.get_app_config('edc_lab')
        return django_apps.get_model(edc_lab_app_config.requisition_model)
