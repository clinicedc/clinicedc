from django.conf import settings

view_subjectconsent = ".view_".join(settings.SUBJECT_CONSENT_MODEL.split("."))
add_subjectconsent = ".add_".join(settings.SUBJECT_CONSENT_MODEL.split("."))
change_subjectconsent = ".change_".join(settings.SUBJECT_CONSENT_MODEL.split("."))
delete_subjectconsent = ".delete_".join(settings.SUBJECT_CONSENT_MODEL.split("."))
view_historicalsubjectconsent = ".view_historical".join(
    settings.SUBJECT_CONSENT_MODEL.split(".")
)


pii = [
    view_subjectconsent,
    add_subjectconsent,
    change_subjectconsent,
    delete_subjectconsent,
    view_historicalsubjectconsent,
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
