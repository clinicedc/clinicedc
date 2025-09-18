import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style

style = color_style()


def post_migrate_user_groups_and_roles(sender=None, **kwargs):
    """Update Groups, Role model with EDC defaults."""

    from .auth_updater import AuthUpdater
    from .auth_updater.group_updater import CodenameDoesNotExist

    try:
        AuthUpdater(apps=django_apps, verbose=True)
    except CodenameDoesNotExist as e:
        sys.stdout.write(style.ERROR(f"{e}. "))
        sys.stdout.write(
            style.ERROR(
                "\n\nIf the codename is mispelled, correct the error and try again.\n\n"
            )
        )
        sys.stdout.write(
            style.ERROR(
                "\nIf the codename is a custom codename (not Django's), "
                "make sure you created it.\n\n"
            )
        )
        sys.stdout.write(
            style.ERROR(
                "\nIf this is happening in a migration that is creating a new model,\n"
                "the post_migrate signal that creates the new model's permissions\n"
                "might be queued to run AFTER edc_auth's post_migrate signal. Let this\n"
                "migration complete and then run `migrate` again.\n\n"
                "If the problem persists, check your code.\n\n"
            )
        )
