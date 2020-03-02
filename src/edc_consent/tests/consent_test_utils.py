from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag

from ..consent import Consent
from ..site_consents import site_consents


def consent_object_factory(
    model=None,
    start=None,
    end=None,
    gender=None,
    updates_versions=None,
    version=None,
    age_min=None,
    age_max=None,
    age_is_adult=None,
):
    options = dict(
        start=start,
        end=end,
        gender=gender or ["M", "F"],
        updates_versions=updates_versions or [],
        version=version or "1",
        age_min=age_min or 16,
        age_max=age_max or 64,
        age_is_adult=age_is_adult or 18,
    )
    model = model or "edc_consent.subjectconsent"
    consent = Consent(model, **options)
    site_consents.register(consent)
    return consent


def consent_factory(**kwargs):
    options = dict(
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        gender=kwargs.get("gender", ["M", "F"]),
        updates_versions=kwargs.get("updates_versions", []),
        version=kwargs.get("version", "1"),
        age_min=kwargs.get("age_min", 16),
        age_max=kwargs.get("age_max", 64),
        age_is_adult=kwargs.get("age_is_adult", 18),
    )
    model = kwargs.get("model", "edc_consent.subjectconsent")
    consent = Consent(model, **options)
    site_consents.register(consent)
    return consent
