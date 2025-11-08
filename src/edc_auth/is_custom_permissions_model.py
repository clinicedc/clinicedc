from .model_mixins import EdcPermissionsModelMixin


def is_custom_permissions_model(model=None) -> bool:
    """Returns True if model is a permissions model."""
    return issubclass(model, (EdcPermissionsModelMixin,))
