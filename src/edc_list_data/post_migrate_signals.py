import sys

from django.core.management.color import color_style

style = color_style()


def post_migrate_list_data(sender=None, **kwargs):
    from .site_list_data import get_autodiscover_enabled, site_list_data  # noqa: PLC0415

    if get_autodiscover_enabled():
        sys.stdout.write(style.MIGRATE_HEADING("Updating list data:\n"))
        site_list_data.load_data()
        sys.stdout.write("Done.\n")
        sys.stdout.flush()
