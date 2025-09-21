from django.apps import apps as django_apps

from edc_auth.constants import ACCOUNT_MANAGER_ROLE
from edc_auth.site_auths import site_auths
from edc_export.constants import EXPORT

from .auth_objects import NOTIFICATION, codenames


def update_site_auths():
    site_auths.add_group(*codenames, name=NOTIFICATION)
    if django_apps.is_installed("edc_export"):
        site_auths.update_group("edc_notification.export_notification", name=EXPORT)
    site_auths.update_role(NOTIFICATION, name=ACCOUNT_MANAGER_ROLE)


update_site_auths()
