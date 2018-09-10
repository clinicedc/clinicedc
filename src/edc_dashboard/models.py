from django.conf import settings
from edc_base.model_mixins import BaseUuidModel


class Dashboard(BaseUuidModel):

    pass


if settings.APP_NAME == 'edc_dashboard':
    from .tests import models
