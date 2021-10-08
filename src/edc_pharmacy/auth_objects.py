from django.apps import apps as django_apps

app_name = "edc_pharmacy"
DISPENSING = "DISPENSING"
PHARMACY = "PHARMACY"
PHARMACY_VIEW = "PHARMACY_VIEW"
DISPENSING_VIEW = "DISPENSING_VIEW"
PHARMACIST_ROLE = "pharmacist"
SITE_PHARMACIST_ROLE = "site_pharmacist"

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
pharmacy_codenames.sort()

# dispensing_models = [
#     "dispenseditem",
#     "dosageguideline",
#     "medication",
#     "prescription",
#     "prescriptionitem",
# ]
# dispensing_codenames = []
# for model_name in dispensing_models:
#     dispensing_codenames.extend([c for c in pharmacy_codenames if model_name in c])
# dispensing_models.sort()
