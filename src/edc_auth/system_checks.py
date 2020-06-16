import os
import sys

from django.core.checks import Warning
from django.conf import settings
from django.core.management import color_style

style = color_style()


def edc_check(app_configs, **kwargs):
    errors = []
    errors = check_etc_dir(errors)
    errors = check_key_path(errors)
    errors = check_static_root(errors)
    return errors


def check_etc_dir(errors):
    sys.stdout.write(style.SQL_KEYWORD("check_etc_dir ... \r"))
    try:
        settings.ETC_DIR
    except AttributeError:
        pass
    else:
        if (
            not settings.DEBUG
            and settings.ETC_DIR
            and not settings.ETC_DIR.startswith("/etc")
        ):
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
    sys.stdout.write(style.SQL_KEYWORD("check_etc_dir ... done.\n"))
    return errors


def check_static_root(errors):
    sys.stdout.write(style.SQL_KEYWORD("check_static_root ... \r"))
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
    sys.stdout.write(style.SQL_KEYWORD("check_static_root ... done.\n"))
    return errors


def check_key_path(errors):
    sys.stdout.write(style.SQL_KEYWORD("check_key_path ...\r"))
    try:
        settings.KEY_PATH
    except AttributeError:
        pass
    else:
        if settings.KEY_PATH and os.access(settings.KEY_PATH, os.W_OK):
            errors.append(
                Warning(
                    "Insecure configuration. Folder is writeable by this user. "
                    f"Got {settings.KEY_PATH}",
                    id="settings.KEY_PATH",
                )
            )
    sys.stdout.write(style.SQL_KEYWORD("check_key_path ... done.\n"))
    return errors
