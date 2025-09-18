import sys

from django.core.management.color import color_style

style = color_style()


def update_action_types(sender=None, verbose=None, **kwargs):
    from .site_action_items import site_action_items

    sys.stdout.write(style.MIGRATE_HEADING("Updating action types:\n"))
    site_action_items.create_or_update_action_types()
    sys.stdout.write("Done.\n")
    sys.stdout.flush()
