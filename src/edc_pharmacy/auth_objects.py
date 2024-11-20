from django.apps import apps as django_apps

app_name = "edc_pharmacy"
# groups
DISPENSING = "DISPENSING"
DISPENSING_VIEW = "DISPENSING_VIEW"
PHARMACY = "PHARMACY"
PHARMACY_PRESCRIBER = "PHARMACY_PRESCRIBER"
PHARMACY_VIEW = "PHARMACY_VIEW"

# roles
CENTRAL_PHARMACIST_ROLE = "CENTRAL_PHARMACIST_ROLE"
PHARMACIST_ROLE = "PHARMACIST_ROLE"
PHARMACY_AUDITOR_ROLE = "PHARMACY_AUDITOR_ROLE"
PHARMACY_PRESCRIBER_ROLE = "PHARMACY_PRESCRIBER_ROLE"
SITE_PHARMACIST_ROLE = "SITE_PHARMACIST_ROLE"

pharmacy_codenames = ["edc_pharmacy.view_subject"]
prescriber_codenames = ["edc_pharmacy.view_subject"]

pharmacy_navbar_codenames = [
    "edc_pharmacy.nav_pharmacy_section",
]

pharmacy_navbar_tuples = []
for codename in pharmacy_navbar_codenames:
    pharmacy_navbar_tuples.append((codename, f"Can access {codename.split('.')[1]}"))


for app_config in django_apps.get_app_configs():
    if app_config.name in [
        "edc_pharmacy",
    ]:
        for model_cls in app_config.get_models():
            app_name, model_name = model_cls._meta.label_lower.split(".")
            if model_name == "registeredsubjectproxy":
                continue
            for prefix in ["add", "change", "view", "delete"]:
                pharmacy_codenames.append(f"{app_name}.{prefix}_{model_name}")

for model_name in ["dosageguideline", "formulation", "medication", "rxrefill"]:
    prescriber_codenames.extend(
        [
            c
            for c in pharmacy_codenames
            if model_name in c and c.startswith("edc_pharmacy.view")
        ]
    )
for model_name in ["rx", "rxitem"]:
    prescriber_codenames.extend([c for c in pharmacy_codenames if model_name in c])

prescriber_codenames.extend(pharmacy_navbar_codenames)
pharmacy_codenames.extend(pharmacy_navbar_codenames)
prescriber_codenames.sort()
pharmacy_codenames.sort()
