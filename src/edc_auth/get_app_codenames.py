from __future__ import annotations

from django.apps import apps as django_apps


def get_models(app_config, exclude_models: list[str] | None):
    exclude_models = exclude_models or []
    return [m for m in app_config.get_models() if m._meta.label_lower not in exclude_models]


def get_app_codenames(
    *crud_apps: str,
    list_app: str | None = None,
    autocomplete_models: list[str] | None = None,
    permissions: list[str] | None = None,
    exclude_models: list[str] | tuple[str, ...] | None = None,
    include_import_export: bool | None = None,
) -> list[str]:
    """Prepares and returns an ordered list of codenames for the
    common edc project apps to be used in `auth_objects`.

    Reads default_permissions from model.Meta or permissions
    to build a list of codenames for each model in the app_config.

    For example, in `auths.py`:

        clinic_codenames = get_app_codenames(
            "meta_prn", "meta_subject", "meta_consent", list_app="meta_lists"
        )
    """

    codenames: list[str] = []
    autocomplete_models = autocomplete_models or []
    exclude_models = exclude_models or []
    try:
        app_config = django_apps.get_app_config(list_app)
    except LookupError:
        pass
    else:
        for model_cls in get_models(app_config, exclude_models):
            codenames.append(f"{app_config.name}.view_{model_cls._meta.model_name}")
    for name in crud_apps:
        try:
            app_config = django_apps.get_app_config(name)
        except LookupError:
            pass
        else:
            for model_cls in get_models(app_config, exclude_models):
                codenames.extend(
                    get_codename(
                        app_config.name,
                        model_cls,
                        autocomplete_models,
                        override_permissions=permissions,
                        include_import_export=include_import_export,
                    )
                )
    codenames.sort()
    return codenames


def get_codename(
    app_name,
    model_cls,
    autocomplete_models: list[str] | None = None,
    override_permissions: list[str] | None = None,
    include_import_export: bool | None = None,
) -> list[str]:
    codenames = []
    autocomplete_models = autocomplete_models or []
    label_lower: str = model_cls._meta.label_lower
    model_name: str = model_cls._meta.model_name
    if "historical" in label_lower or label_lower in autocomplete_models:
        codenames.append(f"{app_name}.view_{model_name}")
    else:
        permissions = override_permissions or model_cls._meta.default_permissions
        if not include_import_export:
            permissions = [
                x for x in permissions if x not in ["export", "import", "viewallsites"]
            ]
        prefixes = [f"{s}_" for s in permissions]
        for prefix in prefixes:
            codenames.append(f"{app_name}.{prefix}{model_name}")
    return codenames
