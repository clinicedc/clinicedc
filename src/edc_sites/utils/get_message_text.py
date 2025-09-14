from django.contrib import messages
from django.utils.translation import gettext as _


def get_message_text(level: int) -> str:
    if level == messages.WARNING:
        return _(
            "You have permissions to view forms and data from sites other than the current. "
        )
    if level == messages.ERROR:
        return _(
            "Showing data from the current site only. Although you have permissions to view "
            "data from multiple sites you also have permissions to add, change or delete "
            "data. This is not permitted when viewing data from multiple sites. Contact your "
            "system administrator."
        )
    return ""
