from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.dispatch import receiver
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..exceptions import NotConsentedError
from ..requires_consent import RequiresConsent


@receiver(pre_save, weak=False, dispatch_uid="requires_consent_on_pre_save")
def requires_consent_on_pre_save(instance, raw, using, update_fields, **kwargs):
    if not raw and not update_fields:
        try:
            consent_model = site_visit_schedules.all_post_consent_models[
                instance._meta.label_lower
            ]
        except KeyError:
            pass
        else:
            try:
                subject_identifier = instance.subject_identifier
            except AttributeError:
                subject_identifier = instance.related_visit.subject_identifier
            if consent_model:
                requires_consent = RequiresConsent(
                    model=instance._meta.label_lower,
                    subject_identifier=subject_identifier,
                    report_datetime=instance.report_datetime,
                    consent_model=consent_model,
                )
                instance.consent_version = requires_consent.version
            else:
                try:
                    RegisteredSubject.objects.get(
                        subject_identifier=subject_identifier,
                        consent_datetime__lte=instance.report_datetime,
                    )
                except ObjectDoesNotExist:
                    raise NotConsentedError(
                        f"Subject is not registered or was not registered by this date. "
                        f"Unable to save {instance._meta.label_lower}. "
                        f"Got {instance.subject_identifier} on "
                        f"{instance.report_datetime}."
                    )
