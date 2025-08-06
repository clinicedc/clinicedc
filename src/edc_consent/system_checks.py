from django.core.checks import CheckMessage, Error, Warning

from .consent_definition import ConsentDefinition
from .exceptions import ConsentDefinitionError
from .site_consents import site_consents


def check_consents(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    errors.extend(check_consents_cdef_registered())
    errors.extend(check_consents_models())
    if not errors:
        errors.extend(check_consents_versions())
        errors.extend(check_consents_durations())
    return errors


def check_consents_cdef_registered() -> list[CheckMessage]:
    errors = []
    if not site_consents.registry:
        errors.append(
            Error("No consent definitions have been registered.", id="edc_consent.E001")
        )
    return errors


def check_consents_models() -> list[CheckMessage]:
    """Expect proxy models only in ConsentDefinitions.

    - ConsentDefinition may only be associated with a proxy model.
    - check proxy models use custom 'objects' and 'on_site' model
      managers.
    """
    errors = []
    for cdef in site_consents.registry.values():
        try:
            cdef.model_cls
        except ConsentDefinitionError as e:
            errors.append(Error(str(e), id="edc_consent.E002"))
        else:
            if not cdef.model_cls._meta.proxy:
                errors.append(
                    Error(
                        (
                            f"Consent definition model is not a proxy model. Got {cdef.model}."
                            f"See {cdef.name}"
                        ),
                        id="edc_consent.E003",
                    )
                )
    return errors


def check_consents_versions() -> list[CheckMessage]:
    """Expect versions to be unique across `proxy_for` model"""
    errors = []
    used = []
    for cdef in [cdef for cdef in site_consents.registry.values()]:
        if cdef in used:
            continue
        err, used = _inspect_others_using_same_proxy_for_model_with_duplicate_versions(
            cdef, used
        )
        if err:
            errors.append(err)
    return errors


def check_consents_durations() -> list[CheckMessage]:
    """Durations may not overlap across `proxy_for` model

    This check needs models to be ready otherwise we would add it
    to site_consents.register.
    """
    errors = []
    found = []
    cdefs: list[ConsentDefinition] = [cdef for cdef in site_consents.registry.values()]
    for cdef1 in cdefs:
        for cdef2 in cdefs:
            if cdef1 == cdef2:
                continue
            err, found = _inspect_possible_overlap_in_validity_period(cdef1, cdef2, found)
            if err:
                errors.append(err)
    return errors


def _inspect_possible_overlap_in_validity_period(
    cdef1, cdef2, found
) -> tuple[Warning | None, list]:
    """Durations between cdef1 and cdef2 may not overlap
    if they are using proxies of the same model -- `proxy_for` model.

    This is just a warning as there may be valid cases to allow this.
    For example, where consent definitions are customized by site.
    """
    err = None
    if (
        cdef1.model_cls._meta.proxy
        and cdef1.model_cls._meta.proxy_for_model == cdef1.model_cls._meta.proxy_for_model
    ):
        if cdef1.start <= cdef2.start <= cdef1.end or cdef1.start <= cdef2.end <= cdef1.end:
            if sorted([cdef1, cdef2], key=lambda x: x.version) in found:
                pass
            else:
                found.append(sorted([cdef1, cdef2], key=lambda x: x.version))
                err = Warning(
                    "Consent definition duration overlap found for same proxy_for_model. "
                    f"Got {cdef1.name} and {cdef2.name}.",
                    id="edc_consent.W002",
                )

    return err, found


def _inspect_others_using_same_proxy_for_model_with_duplicate_versions(
    cdef1: ConsentDefinition, used: list[ConsentDefinition]
) -> tuple[Warning | None, list[ConsentDefinition]]:
    err = None
    versions = []
    opts1 = cdef1.model_cls._meta
    for cdef2 in site_consents.registry.values():
        opts2 = cdef2.model_cls._meta
        if opts2.proxy and opts2.proxy_for_model == opts1.proxy_for_model:
            versions.append(cdef2.version)
            used.append(cdef2)
    if duplicates := [v for v in versions if versions.count(v) > 1]:
        err = Warning(
            f"Duplicate consent definition 'version' found for same proxy_for_model. "
            f"Got '{opts1.proxy_for_model._meta.label_lower}' versions {set(duplicates)}.",
            id="edc_consent.W001",
        )
    return err, used
