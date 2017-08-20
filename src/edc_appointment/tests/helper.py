from edc_base.utils import get_utcnow

from .models import SubjectConsent, EnrollmentOne


class Helper:

    def __init__(self, subject_identifier=None):
        self.subject_identifier = subject_identifier

    def consent_and_enroll(self, subject_identifier=None):
        subject_identifier = subject_identifier or self.subject_identifier
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=get_utcnow())
        EnrollmentOne.objects.create(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            is_eligible=True)
