from django.apps import apps as django_apps

LAB_RESULTS_IMPORT = "lab_results_import"

codenames = []
for app_config in django_apps.get_app_configs():
    if app_config.name == "edc_lab_results_import":
        for model_cls in app_config.get_models():
            for prefix in ["add", "change", "delete", "view"]:
                codenames.append(  # noqa: PERF401
                    f"{app_config.name}.{prefix}_{model_cls._meta.model_name}"
                )
codenames.sort()
