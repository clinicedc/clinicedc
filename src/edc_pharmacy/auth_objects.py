from edc_pharmacy.utils import get_codenames

# groups
DISPENSING = "DISPENSING"
DISPENSING_VIEW = "DISPENSING_VIEW"
PHARMACY = "PHARMACY"
PHARMACY_SITE = "PHARMACY_SITE"
PHARMACY_PRESCRIBER = "PHARMACY_PRESCRIBER"
PHARMACY_VIEW = "PHARMACY_VIEW"
PHARMACY_SUPER = "PHARMACY_SUPER"

# roles
CENTRAL_PHARMACIST_ROLE = "CENTRAL_PHARMACIST_ROLE"
PHARMACIST_ROLE = "PHARMACIST_ROLE"
PHARMACY_AUDITOR_ROLE = "PHARMACY_AUDITOR_ROLE"
PHARMACY_PRESCRIBER_ROLE = "PHARMACY_PRESCRIBER_ROLE"
SITE_PHARMACIST_ROLE = "SITE_PHARMACIST_ROLE"
PHARMACY_SUPER_ROLE = "PHARMACY_SUPER_ROLE"

navbar_codenames = ["edc_pharmacy.nav_pharmacy_section"]
navbar_tuples = []
for codename in navbar_codenames:
    navbar_tuples.append((codename, f"Can access {codename.split('.')[1]}"))


# central pharmacist
view_only_models = [
    "edc_pharmacy.confirmation",
    "edc_pharmacy.allocation",
    "edc_pharmacy.formulation",
    "edc_pharmacy.formulationtype",
    "edc_pharmacy.frequencyunits",
    "edc_pharmacy.location",
    "edc_pharmacy.medication",
    "edc_pharmacy.stock",
    "edc_pharmacy.stockavailability",
    "edc_pharmacy.assignment",
    "edc_pharmacy.subject",
    "edc_pharmacy.visitschedule",
]
pharmacy_codenames = get_codenames([], view_only_models=view_only_models)
pharmacy_codenames.extend(navbar_codenames)
pharmacy_codenames.sort()


# site pharmacist
exclude_models = [
    "edc_pharmacy.lot",
    "edc_pharmacy.assignment",
    "edc_pharmacy.order",
    "edc_pharmacy.orderitem",
    "edc_pharmacy.receive",
    "edc_pharmacy.receiveitem",
]
view_only_models = [
    "edc_pharmacy.stocktransferproxy",
    "edc_pharmacy.stocktransferitem",
    "edc_pharmacy.confirmation",
    "edc_pharmacy.allocation",
    "edc_pharmacy.allocationproxy",
    "edc_pharmacy.container",
    "edc_pharmacy.containertype",
    "edc_pharmacy.formulation",
    "edc_pharmacy.formulationtype",
    "edc_pharmacy.frequencyunits",
    "edc_pharmacy.location",
    "edc_pharmacy.medication",
    "edc_pharmacy.product",
    "edc_pharmacy.stock",
    "edc_pharmacy.stockavailability",
    "edc_pharmacy.stockadjustment",
    "edc_pharmacy.stockproxy",
    "edc_pharmacy.subject",
    "edc_pharmacy.visitschedule",
]
pharmacy_site_codenames = get_codenames(
    [], view_only_models=view_only_models, exclude_models=exclude_models
)
pharmacy_site_codenames.extend(navbar_codenames)
pharmacy_site_codenames.sort()

# prescriber
prescriber_codenames = []
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
prescriber_codenames.append("edc_pharmacy.view_subject")
prescriber_codenames.sort()
