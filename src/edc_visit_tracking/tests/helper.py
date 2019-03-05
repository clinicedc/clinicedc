from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .models import SubjectConsent


class Helper:
    def __init__(self, subject_identifier=None):
        self.subject_identifier = subject_identifier

    def consent_and_put_on_schedule(self, subject_identifier=None):
        subject_identifier = subject_identifier or self.subject_identifier
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier, consent_datetime=get_utcnow()
        )
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_visit_tracking.onscheduleone"
        )
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
