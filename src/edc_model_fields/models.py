from django.conf import settings

if settings.APP_NAME == "edc_model_fields":
    from .tests.models import TestModel  # noqa
