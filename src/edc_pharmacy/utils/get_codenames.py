from django.apps import apps as django_apps


def get_codenames(
    codenames: list[str],
    view_only_models: list[str] | None = None,
    exclude_models: list[str] | None = None,
) -> list[str]:
    """Return a list of all codenames for the role.

    See auths.py
    """
    view_only_models = view_only_models or []
    exclude_models = exclude_models or []
    for app_config in django_apps.get_app_configs():
        if app_config.name in ["edc_pharmacy"]:
            for model_cls in app_config.get_models():
                label_lower = model_cls._meta.label_lower
                app_name, model_name = label_lower.split(".")
                if label_lower in exclude_models:
                    continue
                if label_lower in view_only_models:
                    codenames.append(f"{app_name}.view_{model_name}")
                else:
                    for prefix in ["view_", "add_", "change_", "delete_"]:
                        codenames.append(f"{app_name}.{prefix}{model_name}")
    return codenames
