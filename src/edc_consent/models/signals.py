from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from edc_sites import site_sites
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.subject_schedule import SubjectSchedule

from ..model_mixins import ConsentExtensionModelMixin, RequiresConsentFieldsModelMixin
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
            consent_definition=consent_definition,
        )
        version = consent_definition.version
        if (
            consent_definition.extended_by
            and consent_definition.extended_by.start <= instance.report_datetime
            and consent_definition.extended_by.get_consent_extension_for(
                subject_identifier=subject_identifier,
                site_id=instance.site_id,
            )
        ):
            version = consent_definition.extended_by.version
        instance.consent_version = version
        instance.consent_model = consent_definition.model


@receiver(
    post_save,
    weak=False,
    dispatch_uid="update_appointment_from_consentext_post_save",
)
def update_appointment_from_consentext_post_save(
    sender, instance, raw, created, using, **kwargs
):
    if (
        not raw
        and not kwargs.get("update_fields")
        and isinstance(instance, (ConsentExtensionModelMixin,))
    ):
        cdef = site_consents.get_consent_definition(
            model=instance.subject_consent._meta.label_lower,
            version=instance.subject_consent.version,
        )
        visit_schedule, schedule = site_visit_schedules.get_by_consent_definition(cdef)
        subject_schedule = SubjectSchedule(
            instance.subject_consent.subject_identifier,
            visit_schedule=visit_schedule,
            schedule=schedule,
        )
        subject_schedule.refresh_appointments()
