from __future__ import annotations

import warnings

from edc_auth.get_app_codenames import get_app_codenames

warnings.warn(
    "This path/func name is deprecated in favor of get_app_codenames.get_app_codenames.",
    DeprecationWarning,
    stacklevel=2,
)


def get_clinic_codenames(
    *crud_apps: str,
    list_app: str | None = None,
    autocomplete_models: list[str] | None = None,
):
    return get_app_codenames(
        *crud_apps,
        list_app=list_app,
        autocomplete_models=autocomplete_models,
    )
