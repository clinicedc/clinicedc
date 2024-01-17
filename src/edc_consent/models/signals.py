from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.dispatch import receiver
from edc_registration.models import RegisteredSubject
from edc_sites import site_sites

from ..exceptions import NotConsentedError
from ..model_mixins import RequiresConsentFieldsModelMixin
from ..utils import get_consent_or_raise


@receiver(pre_save, weak=False, dispatch_uid="requires_consent_on_pre_save")
def requires_consent_on_pre_save(instance, raw, using, update_fields, **kwargs):
    if (
        not raw
        and not update_fields
        and isinstance(instance, (RequiresConsentFieldsModelMixin,))
        and not instance._meta.model_name.startswith("historical")
    ):
        subject_identifier = getattr(instance, "related_visit", instance).subject_identifier
        schedule = getattr(instance, "related_visit", instance).schedule
        site = getattr(instance, "related_visit", instance).site
        # is the subject registered?
        try:
            RegisteredSubject.objects.get(
                subject_identifier=subject_identifier,
                consent_datetime__lte=instance.report_datetime,
            )
        except ObjectDoesNotExist:
            raise NotConsentedError(
                f"Subject is not registered or was not registered by this date. "
                f"Unable to save {instance._meta.label_lower}. "
                f"Got {subject_identifier} on "
                f"{instance.report_datetime}."
            )

        # get the consent definition valid for this report_datetime.
        # Schedule may have more than one consent definition but only one
        # is returned
        consent_definition = schedule.get_consent_definition(
            site=site_sites.get(site.id), report_datetime=instance.report_datetime
        )
        get_consent_or_raise(
            model=instance._meta.label_lower,
            subject_identifier=subject_identifier,
            report_datetime=instance.report_datetime,
            consent_definition=consent_definition,
        )
        instance.consent_version = consent_definition.version
