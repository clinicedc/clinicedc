import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.checks import Warning
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError


def edc_notification_check(app_configs, **kwargs):
    errors = []
    if not getattr(settings, "EMAIL_ENABLED", False):
        errors.append(
            Warning(
                "Notifications by email are disabled.",
                hint="To enable set settings.EMAIL_ENABLED = True",
                id="edc_notification.W002",
            )
        )
    try:
        if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
            users = get_user_model().objects.filter(
                (
                    Q(first_name__isnull=True)
                    | Q(last_name__isnull=True)
                    | Q(email__isnull=True)
                ),
                is_active=True,
                is_staff=True,
            )
            try:
                for user in users:
                    errors.append(
                        Warning(
                            (
                                f"User account is incomplete. Check that first name, "
                                f"last name and email are complete. See {user}"
                            ),
                            hint="Complete the user's account details.",
                            obj=get_user_model(),
                            id="edc_notification.W001",
                        )
                    )
            except OperationalError:
                pass
    except ProgrammingError:
        pass
    return errors
