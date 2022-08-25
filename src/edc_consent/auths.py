from django.conf import settings
from edc_auth.auth_objects import PII, PII_VIEW
from edc_auth.site_auths import site_auths
from edc_auth.utils import remove_default_model_permissions_from_edc_permissions

from .auth_objects import consent_codenames, navbar_tuples

site_auths.add_post_update_func(
    "edc_consent",
    remove_default_model_permissions_from_edc_permissions,
)

site_auths.add_custom_permissions_tuples(
    model="edc_consent.edcpermissions", codename_tuples=navbar_tuples
)

site_auths.update_group(*consent_codenames, name=PII, no_delete=True)
site_auths.update_group(*consent_codenames, name=PII_VIEW, view_only=True)
site_auths.add_pii_model(settings.SUBJECT_CONSENT_MODEL)
