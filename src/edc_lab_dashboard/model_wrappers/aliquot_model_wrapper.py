from edc_lab.models import Aliquot, BoxItem, ManifestItem
from edc_model_wrapper import ModelWrapper


class AliquotModelWrapper(ModelWrapper):

    model_cls = Aliquot
    next_url_name = "aliquot_listboard_url"

    @property
    def human_readable_identifier(self):
        return self.object.human_readable_identifier

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
                    identifier=self.box_item.box.box_identifier
                )
            except ManifestItem.DoesNotExist:
                pass
        return manifest_item
