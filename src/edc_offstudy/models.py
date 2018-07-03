from django.conf import settings
from edc_base.model_mixins.base_uuid_model import BaseUuidModel

from .model_mixins import OffstudyModelMixin


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

    pass


if settings.APP_NAME == 'edc_offstudy':
    from .tests import models
