from django.contrib import messages
from django.utils.translation import gettext as _


def get_message_text(level: int) -> str:
    if level == messages.INFO:
        return _(
            "You have permissions to view data from multiple sites. "
            "The data showing may not be from the current site"
        )
    elif level == messages.WARNING:
        return _(
            "Showing data from the current site only. Although you have permissions to view "
            "data from multiple sites you also have permissions to add, change or delete "
            "data. This is not permitted when viewing data from multiple sites."
        )
    return ""
