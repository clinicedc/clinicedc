from django.db import models
from django.utils import timezone

from edc_model.models import BaseUuidModel
from edc_randomization.model_mixins import RandomizationListModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_sites.model_mixins import SiteModelMixin


class SubjectConsent(UpdatesOrCreatesRegistrationModelMixin, SiteModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    initials = models.CharField(max_length=25)

    consent_datetime = models.DateTimeField(default=timezone.now)

    gender = models.CharField(max_length=25, default="")


class MyRandomizationList(RandomizationListModelMixin, BaseUuidModel):
    class Meta(RandomizationListModelMixin.Meta):
        pass
