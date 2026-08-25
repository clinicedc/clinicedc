from django.conf import settings


def get_prn_app_label() -> str:
    return getattr(settings, "PRN_APP_LABEL", f"{settings.APP_NAME.lower()}_prn")


def get_prn_admin_site_name() -> str:
    return getattr(settings, "PRN_ADMIN_SITE_NAME", f"{get_prn_app_label()}_admin")
