from django.db import models

from edc_base.model.models import BaseUuidModel

from ..managers import BaseConsentHistoryManager


class BaseConsentHistory(BaseUuidModel):

    """A base class for the edc_consent history.

    Ties in with the edc_consent model method :func:get_consent_history_model`,
    the manager method above and a signal in :mod:`edc_consent.models.signals`
    """

    subject_identifier = models.CharField(max_length=50)
    consent_datetime = models.DateTimeField()
    consent_pk = models.CharField(max_length=50)
    consent_app_label = models.CharField(max_length=50)
    consent_model_name = models.CharField(max_length=50)

    objects = BaseConsentHistoryManager()

    class Meta:
        abstract = True
