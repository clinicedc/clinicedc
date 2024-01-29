import sys

from django.core.management.color import color_style

style = color_style()


def post_migrate_update_sites(sender=None, **kwargs):
    from .site import sites as site_sites
    from .utils import add_or_update_django_sites

    sys.stdout.write(style.MIGRATE_HEADING("Updating sites:\n"))

    for country in site_sites.countries:
        sys.stdout.write(style.MIGRATE_HEADING(f" (*) sites for {country} ...\n"))
        add_or_update_django_sites(verbose=True)
    sys.stdout.write("Done.\n")
    sys.stdout.flush()
