from .metadata_helper_mixin import MetadataHelperMixin


class MetadataHelper(MetadataHelperMixin):
    metadata_helper_instance_attr = "instance"

    def __init__(self, instance):
        self.instance = instance
