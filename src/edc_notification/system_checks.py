import sys

from django.contrib.auth import get_user_model
from django.core.checks import Warning, register
from django.core.management import color_style
from django.db.models import Q
from django.db.utils import ProgrammingError, OperationalError

style = color_style()


@register()
def edc_notification_check(app_configs, **kwargs):
    sys.stdout.write(style.SQL_KEYWORD("edc_notification_check ...\r"))
    errors = []
    try:
        if "migrate" not in sys.argv and "makemigrations" not in sys.argv:
            User = get_user_model()
            users = User.objects.filter(
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
                            obj=User,
                            id="edc_notification.W001",
                        )
                    )
            except OperationalError:
                pass
    except ProgrammingError:
        pass
    sys.stdout.write(style.SQL_KEYWORD("edc_notification_check ... done\n"))
    return errors
