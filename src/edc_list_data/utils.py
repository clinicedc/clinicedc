from django.conf import settings


def get_list_model_app() -> str:
    """Returns the list model module name, e.g. meta_lists."""
    return settings.LIST_MODEL_APP_LABEL
