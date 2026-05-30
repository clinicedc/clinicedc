from django.apps import apps as django_apps

LAB_RESULTS = "LAB_RESULTS"

lab_results_codenames = []
for app_config in django_apps.get_app_configs():
    if app_config.name in ["edc_lab_results"]:
        for model_cls in app_config.get_models():
            for prefix in ["add", "change", "delete", "view"]:
                lab_results_codenames.append(
                    f"{app_config.name}.{prefix}_{model_cls._meta.model_name}"
                )
lab_results_codenames.sort()
