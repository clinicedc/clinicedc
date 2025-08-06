import os

from django.conf import settings
from django.core.checks import CheckMessage, Warning
from django.core.management import color_style

style = color_style()


def check_etc_dir(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    try:
        settings.ETC_DIR
    except AttributeError:
        pass
    else:
        if not settings.DEBUG and settings.ETC_DIR and not settings.ETC_DIR.startswith("/etc"):
            errors.append(
                Warning(
                    "Insecure configuration. Use root level etc folder. "
                    f"For example, '/etc/{settings.APP_NAME}/' "
                    f"Got {settings.ETC_DIR}",
                    id="settings.ETC_DIR",
                )
            )
        if settings.ETC_DIR and os.access(settings.ETC_DIR, os.W_OK):
            errors.append(
                Warning(
                    "Insecure configuration. Folder is writeable by this user. "
                    f"Got {settings.ETC_DIR}",
                    id="settings.ETC_DIR",
                )
            )
    return errors


def check_static_root(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    try:
        settings.STATIC_ROOT
    except AttributeError:
        pass
    else:
        if settings.STATIC_ROOT and not os.path.exists(settings.STATIC_ROOT):
            errors.append(
                Warning(
                    f"Folder does not exist. Got {settings.STATIC_ROOT}",
                    id="settings.STATIC_ROOT",
                )
            )
    return errors


def check_auth_updater(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    try:
        settings.EDC_AUTH_SKIP_AUTH_UPDATER
    except AttributeError:
        pass
    else:
        if settings.EDC_AUTH_SKIP_AUTH_UPDATER:
            errors.append(
                Warning(
                    "AuthUpdater did not load. Groups and permissions have not been updated. "
                    "See settings.EDC_AUTH_SKIP_AUTH_UPDATER.",
                    id="settings.EDC_AUTH_SKIP_AUTH_UPDATER",
                )
            )
    return errors


def check_site_auths(app_configs, **kwargs) -> list[CheckMessage]:
    errors = []
    try:
        settings.EDC_AUTH_SKIP_AUTH_UPDATER
    except AttributeError:
        pass
    else:
        if settings.EDC_AUTH_SKIP_AUTH_UPDATER:
            errors.append(
                Warning(
                    "SiteAuths did not autodiscover. Groups and permissions data not ready "
                    "for AuthUpdater. See settings.EDC_AUTH_SKIP_SITE_AUTHS.",
                    id="settings.EDC_AUTH_SKIP_SITE_AUTHS",
                )
            )
    return errors
