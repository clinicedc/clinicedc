import contextlib
import sys

from django.contrib.auth import get_user_model
from django.core.checks import Warning as DjangoWarning
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError

from .utils import get_email_enabled


def edc_notification_check(app_configs, **kwargs):
    errors = []
    if not get_email_enabled():
        errors.append(
            DjangoWarning(
                "Notifications by email are disabled.",
                hint="To enable set settings.EDC_MAIL_ENABLED = True",
                id="edc_notification.W002",
            )
        )
    try:
        if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
            users = get_user_model().objects.filter(
                (
                    Q(first_name__isnull=True)
                    | Q(first_name="")
                    | Q(last_name__isnull=True)
                    | Q(last_name="")
                    | Q(email__isnull=True)
                    | Q(email="")
                ),
                is_active=True,
                is_staff=True,
            )
            with contextlib.suppress(OperationalError):
                errors.extend(
                    DjangoWarning(
                        (
                            f"User account is incomplete. Check that first name, "
                            f"last name and email are complete. See {user}"
                        ),
                        hint="Complete the user's account details.",
                        obj=get_user_model(),
                        id="edc_notification.W001",
                    )
                    for user in users
                )
    except ProgrammingError:
        pass
    return errors
