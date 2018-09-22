import sys

from django.conf import settings
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins.base_uuid_model import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin
from edc_offstudy.model_mixins import OffstudyModelManager

from .model_mixins import OffstudyModelMixin


class SubjectOffstudy(OffstudyModelMixin, SiteModelMixin, BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = OffstudyModelManager()

    history = HistoricalRecords()


if 'edc_offstudy' in settings.APP_NAME and 'makemigrations' not in sys.argv:
    from .tests import models
