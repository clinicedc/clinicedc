from django.db import models
from django.core.exceptions import ImproperlyConfigured


class BaseConsentHistoryManager(models.Manager):

    def update_consent_history(self, consent_inst, created, using):
        """Override to save using the edc_consent instance (get_or_create).

        Add this method to your model manager if you have defined a Consent History model and
        configured your edc_consent model to return the edc_consent history model.

        For example::

            def update(self, consent_inst, created, using):
                options = {'consent_datetime': consent_inst.consent_datetime}
                inst, created = super(ConsentHistoryManager, self).using(using).get_or_create(
                    registered_subject=consent_inst.registered_subject,
                    consent_app_label=consent_inst._meta.app_label,
                    consent_model_name=consent_inst._meta.object_name,
                    consent_pk=consent_inst.pk,
                    defaults=options
                    )
                if not created:
                    inst.consent_datetime = consent_inst.consent_datetime
                    inst.save(using=using)

        .. seealso:: :func:`get_consent_history_model` on the edc_consent."""
        raise ImproperlyConfigured('Expected this method to be overridden by user {0}. '
                                   'Got args=(instance={1}, created={2}, using={3}).'.format(
                                       self.__class__, consent_inst, created, using))

    def delete_consent_history(self, app_label, model_name, pk, using):
        super(BaseConsentHistoryManager, self).filter(
            consent_app_label=app_label, consent_model_name=model_name, consent_pk=pk).delete()
