from django.conf import settings

default_pii_models = [
    settings.SUBJECT_CONSENT_MODEL,
    "edc_locator.subjectlocator",
    "edc_registration.registeredsubject",
]
