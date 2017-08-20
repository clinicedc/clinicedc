from django.apps import apps as django_apps

from edc_model_wrapper import ModelWrapper

app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class ManifestItemModelWrapper(ModelWrapper):

    model = edc_lab_app_config.manifest_item_model
    next_url_name = app_config.manage_manifest_listboard_url_name
    action_name = 'manage'

    @property
    def manifest_identifier(self):
        return self.object.manifest.manifest_identifier

    @property
    def box_identifier(self):
        return self.object.identifier

    @property
    def box(self):
        return self.box_model.objects.get(box_identifier=self.object.identifier)

    @property
    def box_model(self):
        return django_apps.get_model(edc_lab_app_config.box_model)
