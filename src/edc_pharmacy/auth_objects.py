from django.apps import apps as django_apps

app_name = "edc_pharmacy"
DISPENSING = "DISPENSING"
PHARMACY = "PHARMACY"
PRESCRIBER = "PRESCRIBER"
PHARMACY_VIEW = "PHARMACY_VIEW"
DISPENSING_VIEW = "DISPENSING_VIEW"
PHARMACIST_ROLE = "pharmacist"
SITE_PHARMACIST_ROLE = "site_pharmacist"
PRESCRIBER_ROLE = "prescriber"
PHARMACY_AUDITOR_ROLE = "pharmacy_auditor_role"

prescriber_codenames = []
pharmacy_codenames = []

for app_config in django_apps.get_app_configs():
    if app_config.name in [
        "edc_pharmacy",
    ]:
        for model_cls in app_config.get_models():
            app_name, model_name = model_cls._meta.label_lower.split(".")
            for prefix in ["add", "change", "view", "delete"]:
                if model_name == "subject" and prefix in ["add", "change", "delete"]:
                    pass
                else:
                    pharmacy_codenames.append(f"{app_name}.{prefix}_{model_name}")

for model_name in [
    "dosageguideline",
    "medication",
    "formulation",
]:
    prescriber_codenames.extend(
        [c for c in pharmacy_codenames if model_name in c and c.startswith("view")]
    )
for model_name in [
    "prescription",
    "prescriptionitem",
]:
    prescriber_codenames.extend([c for c in pharmacy_codenames if model_name in c])

prescriber_codenames.sort()
pharmacy_codenames.sort()
