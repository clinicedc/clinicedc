from django.apps import apps as django_apps


app_name = 'edc_lab'
app_config = django_apps.get_app_config(app_name)


class ModelsViewMixin:

    @property
    def aliquot_model(self):
        return django_apps.get_model(*app_config.aliquot_model.split('.'))

    @property
    def box_model(self):
        return django_apps.get_model(*app_config.box_model.split('.'))

    @property
    def box_item_model(self):
        return django_apps.get_model(*app_config.box_item_model.split('.'))

    @property
    def manifest_model(self):
        return django_apps.get_model(*app_config.manifest_model.split('.'))

    @property
    def requisition_model(self):
        return django_apps.get_model(*app_config.requisition_model.split('.'))
