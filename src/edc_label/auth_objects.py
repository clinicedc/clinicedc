from django.apps import apps as django_apps

app_name = "edc_label"
LABELING = "LABELING"

codenames = []
for app_config in django_apps.get_app_configs():
    if app_config.name in [
        app_name,
    ]:
        for model_cls in app_config.get_models():
            app_name, model_name = model_cls._meta.label_lower.split(".")
            for prefix in ["add", "change", "view", "delete"]:
                codenames.append(f"{app_name}.{prefix}_{model_name}")
codenames.sort()
