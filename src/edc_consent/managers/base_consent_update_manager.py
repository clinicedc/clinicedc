from django.db import models


class BaseConsentUpdateManager(models.Manager):

    def get_by_natural_key(self, consent_attr, consent_cls, consent_version, subject_identifier_as_pk):
        consent = consent_cls.objects.get_by_natural_key(subject_identifier_as_pk=subject_identifier_as_pk)
        options = {consent_attr: consent, 'consent_version': consent_version}
        return self.get(**options)
