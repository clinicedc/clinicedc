from __future__ import annotations

from datetime import datetime

from edc_consent.consent import Consent
from edc_consent.site_consents import site_consents


def consent_object_factory(
    model: str | None = None,
    start: datetime = None,
    end: datetime = None,
    gender: list[str] | None = None,
    updates_versions: list[str] | tuple[str] = None,
    version: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    age_is_adult: int | None = None,
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


def consent_factory(model=None, **kwargs):
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
    model = kwargs.get("model", model or "edc_consent.subjectconsent")
    consent = Consent(model, **options)
    site_consents.register(consent)
    return consent
