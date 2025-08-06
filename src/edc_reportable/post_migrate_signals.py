import sys

from django.core.management import color_style

from .utils import load_all_reference_ranges

style = color_style()


def post_migrate_load_reference_ranges(sender=None, **kwargs):  # noqa
    sys.stdout.write(style.MIGRATE_HEADING("Loading reference ranges (reportables):\n"))
    load_all_reference_ranges()
