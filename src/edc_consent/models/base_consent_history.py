from django.db import models
from edc.base.model.models import BaseUuidModel
from edc.subject.registration.models import RegisteredSubject
from edc_consent import BaseConsentHistoryManager


class BaseConsentHistory(BaseUuidModel):

    """A base class for the edc_consent history.

    Ties in with the edc_consent model method :func:get_consent_history_model`, the manager method above
    and a signal in :mod:`edc_consent.models.signals`

    .. note:: this is not a sync model so DO NOT turn off the signal when syncing. You want
              the history instances to be created by the incoming edc_consent instances."""

    registered_subject = models.ForeignKey(RegisteredSubject)
    consent_datetime = models.DateTimeField()
    consent_pk = models.CharField(max_length=50)
    consent_app_label = models.CharField(max_length=50)
    consent_model_name = models.CharField(max_length=50)

    objects = BaseConsentHistoryManager()

    class Meta:
        abstract = True
