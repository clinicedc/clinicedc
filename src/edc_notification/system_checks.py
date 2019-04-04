import sys

from django.apps import apps as django_apps
from django.core.checks import Warning, register
from django.db.models import Q
from django.db.utils import ProgrammingError


@register()
def edc_notification_check(app_configs, **kwargs):
    errors = []
    try:
        if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
            User = django_apps.get_model("auth.user")

            for user in User.objects.filter(
                (
                    Q(first_name__isnull=True)
                    | Q(last_name__isnull=True)
                    | Q(email__isnull=True)
                ),
                is_active=True,
                is_staff=True,
            ):
                errors.append(
                    Warning(
                        (
                            f"User account is incomplete. Check that first name, "
                            f"last name and email are complete. See {user}"
                        ),
                        hint="Complete the user's account details.",
                        obj=User,
                        id="edc_notification.W001",
                    )
                )
    except ProgrammingError:
        pass
    return errors
