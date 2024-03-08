from django.core.checks import CheckMessage, Error, Warning

from .consent_definition import ConsentDefinition
from .site_consents import site_consents


def check_consents_cdef_registered(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    if not site_consents.registry:
        errors.append(
            Error("No consent definitions have been registered.", id="edc_consent.E001")
        )
    return errors


def check_consents_proxy_models(app_configs, **kwargs) -> list[CheckMessage]:
    """Expect proxy models only in ConsentDefinitions"""
    errors = []
    for cdef in site_consents.registry.values():
        if not cdef.model_cls._meta.proxy:
            errors.append(
                Error(
                    (
                        f"Consent definition model is not a proxy model. Got {cdef.model}."
                        f"See {cdef.name}"
                    ),
                    id="edc_consent.E002",
                )
            )
    return errors


def check_consents_versions(app_configs, **kwargs) -> list[CheckMessage]:
    """Expect versions to be unique across `proxy_for` model"""
    errors = []
    cdefs1: list[ConsentDefinition] = [cdef for cdef in site_consents.registry.values()]
    used = []
    for cdef1 in cdefs1:
        if cdef1 in used:
            continue
        versions = []
        for cdef in site_consents.registry.values():
            if (
                cdef.model_cls._meta.proxy
                and cdef.model_cls._meta.proxy_for_model
                == cdef1.model_cls._meta.proxy_for_model
            ):
                versions.append(cdef.version)
                used.append(cdef)
        if versions and len(set(versions)) != len(versions):
            errors.append(
                Warning(
                    "Consent definition version in use already for model. "
                    f"Got {cdef.version}.",
                    id="edc_consent.W001",
                )
            )
    return errors


def check_consents_durations(app_configs, **kwargs) -> list[CheckMessage]:
    """Durations may not overlap across `proxy_for` model"""
    errors = []
    found = []
    cdefs: list[ConsentDefinition] = [cdef for cdef in site_consents.registry.values()]
    for cdef1 in cdefs:
        for cdef2 in cdefs:
            if cdef1 == cdef2:
                continue
            if (
                cdef1.model_cls._meta.proxy
                and cdef1.model_cls._meta.proxy_for_model
                == cdef1.model_cls._meta.proxy_for_model
            ):
                if (
                    cdef1.start <= cdef2.start <= cdef1.end
                    or cdef1.start <= cdef2.end <= cdef1.end
                ):
                    if sorted([cdef1, cdef2], key=lambda x: x.version) in found:
                        continue
                    else:
                        found.append(sorted([cdef1, cdef2], key=lambda x: x.version))
                        errors.append(
                            Warning(
                                "Consent definition duration overlap. "
                                f"Got {cdef1.name} and {cdef2.name}.",
                                id="edc_consent.W002",
                            )
                        )
    return errors
