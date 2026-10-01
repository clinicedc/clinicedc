from django.conf import settings


def get_list_model_app() -> str:
    return getattr(settings.LIST_MODEL_APP_LABEL)
