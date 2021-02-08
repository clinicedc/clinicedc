from edc_protocol import Protocol

from .base_label import BaseLabel


class ManifestLabel(BaseLabel):
    model = "edc_lab.manifest"
    template_name = "manifest"

    @property
    def label_context(self):
        return {
            "barcode_value": self.model_obj.manifest_identifier,
            "manifest_identifier": self.model_obj.human_readable_identifier,
            "protocol": Protocol().protocol,
            "site": str(self.model_obj.site.id),
            "manifest_datetime": self.model_obj.manifest_datetime.strftime("%Y-%m-%d %H:%M"),
            "shipper": self.model_obj.shipper,
            "category": self.model_obj.get_category_display().upper(),
            "site_name": str(self.model_obj.site.siteprofile.title),
        }
