import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.core.management.color import color_style

style = color_style()


def populate_data_dictionary(sender=None, **kwargs):
    from .populate_data_dictionary import populate_data_dictionary_from_sites

    sys.stdout.write(style.MIGRATE_HEADING("Populating data dictionary:\n"))
    if getattr(settings, "EDC_DATA_MANAGER_POPULATE_DATA_DICTIONARY", True):
        populate_data_dictionary_from_sites()
        sys.stdout.write("Done populating data dictionary.\n\n")
    else:
        sys.stdout.write(
            "  not populating. See settings.EDC_DATA_MANAGER_POPULATE_DATA_DICTIONARY\n\n"
        )
    sys.stdout.flush()


def update_query_rule_handlers(sender=None, **kwargs):
    from .site_data_manager import site_data_manager

    sys.stdout.write(
        style.MIGRATE_HEADING("Deactivating query rules with invalid rule handler names:\n")
    )
    handler_names = [x for x in site_data_manager.registry.keys()]
    django_apps.get_model("edc_data_manager.queryrule").objects.exclude(
        rule_handler_name__in=handler_names
    ).update(active=False)
    sys.stdout.write("Done.\n")
    sys.stdout.flush()
