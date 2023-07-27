from __future__ import annotations

from django.apps import apps as django_apps


def get_app_codenames(
    *crud_apps: str,
    list_app: str | None = None,
    autocomplete_models: list[str] | None = None,
) -> list[str]:
    """Prepares and returns an ordered list of codenames for the
    common edc project apps to be used in `auth_objects`.

    For example, in `auths.py`:

        clinic_codenames = get_app_codenames(
            "meta_prn", "meta_subject", "meta_consent", list_app="meta_lists"
        )
    """

    clinic_codenames: list[str] = []
    autocomplete_models = autocomplete_models or []
    try:
        app_config = django_apps.get_app_config(list_app)
    except LookupError:
        pass
    else:
        for model_cls in app_config.get_models():
            model_name: str = model_cls._meta.model_name
            for prefix in ["view"]:
                clinic_codenames.append(f"{app_config.name}.{prefix}_{model_name}")
    for name in crud_apps:
        try:
            app_config = django_apps.get_app_config(name)
        except LookupError:
            pass
        else:
            for model_cls in app_config.get_models():
                label_lower: str = model_cls._meta.label_lower
                model_name: str = model_cls._meta.model_name
                if "historical" in label_lower:
                    clinic_codenames.append(f"{app_config.name}.view_{model_name}")
                elif label_lower in autocomplete_models:
                    clinic_codenames.append(f"{app_config.name}.view_{model_name}")
                else:
                    clinic_codenames.append(f"{app_config.name}.view_{model_name}")
                    for prefix in ["add_", "change_", "delete_"]:
                        clinic_codenames.append(f"{app_config.name}.{prefix}{model_name}")
    clinic_codenames.sort()
    return clinic_codenames
