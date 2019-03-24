from edc_lab.models import Box, ManifestItem
from edc_model_wrapper import ModelWrapper


class ManifestItemModelWrapper(ModelWrapper):

    model_cls = ManifestItem
    next_url_name = "manage_manifest_listboard_url"
    action_name = "manage"

    @property
    def manifest_identifier(self):
        return self.object.manifest.manifest_identifier

    @property
    def box_identifier(self):
        return self.object.identifier

    @property
    def box(self):
        return Box.objects.get(box_identifier=self.object.identifier)
