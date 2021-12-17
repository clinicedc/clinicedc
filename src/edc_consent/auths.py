from django.conf import settings
from edc_auth.auth_objects import PII, PII_VIEW
from edc_auth.site_auths import site_auths

from .auth_objects import consent_codenames

site_auths.update_group(*consent_codenames, name=PII, no_delete=True)
site_auths.update_group(*consent_codenames, name=PII_VIEW, view_only=True)
site_auths.add_pii_model(settings.SUBJECT_CONSENT_MODEL)
