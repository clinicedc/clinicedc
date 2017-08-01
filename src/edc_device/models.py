from django.conf import settings

if settings.APP_NAME == 'edc_device':
    from .tests.models import TestModel, TestModel2, TestModelPermissions
