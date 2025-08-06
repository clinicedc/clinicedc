from django.utils.translation import gettext as _

REQUIRES_CONSENT_FIELDS = (
    "consent_model",
    "consent_version",
)
requires_consent_fieldset_tuple = (
    _("Consent"),
    {"classes": ("collapse",), "fields": REQUIRES_CONSENT_FIELDS},
)
