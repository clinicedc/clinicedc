from django.apps import apps as django_apps
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class Helper:
    def __init__(
        self,
        subject_identifier=None,
        subject_consent_model_cls=None,
        onschedule_model_name=None,
    ):
        self.subject_identifier = subject_identifier
        self.subject_consent_model_cls = subject_consent_model_cls or django_apps.get_model(
            "edc_visit_tracking.subjectconsent"
        )
        self.onschedule_model_name = (
            onschedule_model_name or "edc_visit_tracking.onscheduleone"
        )

    def consent_and_put_on_schedule(
        self,
        subject_identifier=None,
    ):
        subject_identifier = subject_identifier or self.subject_identifier
        subject_consent = self.subject_consent_model_cls.objects.create(
            subject_identifier=subject_identifier, consent_datetime=get_utcnow()
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model(self.onschedule_model_name)
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
