from django.apps import apps as django_apps

from edc_auth.get_app_codenames import get_app_codenames

DEMO_AUDITOR = "DEMO_AUDITOR"
DEMO_CLINIC = "DEMO_CLINIC"
DEMO_CLINIC_SUPER = "DEMO_CLINIC_SUPER"
DEMO_EXPORT = "DEMO_EXPORT"
DEMO_REPORTS = "DEMO_REPORTS"
DEMO_REPORTS_AUDIT = "DEMO_REPORTS_AUDIT"

clinic_codenames = []
screening_codenames = []

reports_codenames = get_app_codenames("demo_reports")

for app_config in django_apps.get_app_configs():
    if app_config.name in ["demo_lists"]:
        for model_cls in app_config.get_models():
            clinic_codenames.append(
                f"{app_config.name}.view_{model_cls._meta.model_name}"
            )

for app_config in django_apps.get_app_configs():
    if app_config.name in [
        "demo_prn",
        "demo_subject",
        "demo_consent",
        "demo_screening",
    ]:
        for model_cls in app_config.get_models():
            if "historical" in model_cls._meta.label_lower:
                clinic_codenames.append(
                    f"{app_config.name}.view_{model_cls._meta.model_name}"
                )
            else:
                for prefix in ["add", "change", "view", "delete"]:
                    clinic_codenames.append(
                        f"{app_config.name}.{prefix}_{model_cls._meta.model_name}"
                    )
clinic_codenames.sort()

for app_config in django_apps.get_app_configs():
    if app_config.name in [
        "demo_screening",
    ]:
        for model_cls in app_config.get_models():
            if "historical" in model_cls._meta.label_lower:
                screening_codenames.append(
                    f"{app_config.name}.view_{model_cls._meta.model_name}"
                )
            else:
                for prefix in ["add", "change", "view", "delete"]:
                    screening_codenames.append(
                        f"{app_config.name}.{prefix}_{model_cls._meta.model_name}"
                    )
screening_codenames.sort()
