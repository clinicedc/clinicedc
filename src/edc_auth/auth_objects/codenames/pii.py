from edc_consent.utils import get_consent_model_name, get_reconsent_model_name

consent_codenames = []
for model in [get_reconsent_model_name(), get_consent_model_name()]:
    for action in ["view_", "add_", "change_", "delete_", "view_historical"]:
        consent_codenames.append(f".{action}".join(model.split(".")))

pii = [
    "edc_locator.add_subjectlocator",
    "edc_locator.change_subjectlocator",
    "edc_locator.delete_subjectlocator",
    "edc_locator.view_historicalsubjectlocator",
    "edc_locator.view_subjectlocator",
    "edc_registration.display_dob",
    "edc_registration.display_firstname",
    "edc_registration.display_identity",
    "edc_registration.display_initials",
    "edc_registration.display_lastname",
    "edc_registration.view_historicalregisteredsubject",
    "edc_registration.view_registeredsubject",
]
pii.extend(consent_codenames)
