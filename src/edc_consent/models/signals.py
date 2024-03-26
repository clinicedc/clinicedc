from django.db.models.signals import pre_save
from django.dispatch import receiver
from edc_sites import site_sites

from ..model_mixins import RequiresConsentFieldsModelMixin
from ..site_consents import site_consents


@receiver(pre_save, weak=False, dispatch_uid="requires_consent_on_pre_save")
def requires_consent_on_pre_save(instance, raw, using, update_fields, **kwargs):
    if (
        not raw
        and not update_fields
        and isinstance(instance, (RequiresConsentFieldsModelMixin,))
        and not instance._meta.model_name.startswith("historical")
    ):
        subject_identifier = getattr(instance, "related_visit", instance).subject_identifier
        site = getattr(instance, "related_visit", instance).site
        try:
            schedule = getattr(instance, "related_visit", instance).schedule
        except AttributeError:
            schedule = None
        if schedule:
            consent_definition = schedule.get_consent_definition(
                site=site_sites.get(site.id), report_datetime=instance.report_datetime
            )
        else:
            # this is a PRN model, like SubjectLocator, with no visit_schedule
            consent_definition = site_consents.get_consent_definition(
                site=site_sites.get(site.id), report_datetime=instance.report_datetime
            )
        site_consents.get_consent_or_raise(
            subject_identifier=subject_identifier,
            report_datetime=instance.report_datetime,
            site_id=site.id,
        )
        instance.consent_version = consent_definition.version
        instance.consent_model = consent_definition.model
