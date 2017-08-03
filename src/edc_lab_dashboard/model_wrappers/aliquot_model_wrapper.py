from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper
from edc_lab.models import BoxItem, ManifestItem


app_config = django_apps.get_app_config('edc_lab_dashboard')
edc_lab_app_config = django_apps.get_app_config('edc_lab')


class AliquotModelWrapper(ModelWrapper):

    model = edc_lab_app_config.aliquot_model
    next_url_name = app_config.aliquot_listboard_url_name

    @property
    def human_aliquot_identifier(self):
        return self.object.human_aliquot_identifier

    @property
    def box_item(self):
        try:
            return BoxItem.objects.get(identifier=self.aliquot_identifier)
        except BoxItem.DoesNotExist:
            return None

    @property
    def manifest_item(self):
        manifest_item = None
        if self.box_item:
            try:
                manifest_item = ManifestItem.objects.get(
                    identifier=self.box_item.box.box_identifier)
            except ManifestItem.DoesNotExist:
                pass
        return manifest_item
