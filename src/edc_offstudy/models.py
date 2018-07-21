import sys

from django.conf import settings
from edc_base.model_mixins.base_uuid_model import BaseUuidModel

from .model_mixins import OffstudyModelMixin


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

    pass


if 'edc_offstudy' in settings.APP_NAME and 'makemigrations' not in sys.argv:
    from .tests import models
