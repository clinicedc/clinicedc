from django.db import models
from edc_model.models import BaseUuidModel
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow

from edc_randomization.model_mixins import RandomizationListModelMixin

from .randomizers import MyRandomizer


class SubjectConsent(UpdatesOrCreatesRegistrationModelMixin, SiteModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    initials = models.CharField(max_length=25)

    consent_datetime = models.DateTimeField(default=get_utcnow)

    gender = models.CharField(max_length=25, null=True)


class MyRandomizationList(RandomizationListModelMixin, BaseUuidModel):
    randomizer_cls = MyRandomizer

    class Meta(RandomizationListModelMixin.Meta):
        pass
