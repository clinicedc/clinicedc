import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register
from django.core.management.color import color_style
from django.db.models.signals import post_migrate
from edc_action_item import site_action_items
from edc_action_item.apps import update_action_types
from edc_auth.post_migrate_signals import post_migrate_user_groups_and_roles
from edc_data_manager.populate_data_dictionary import populate_data_dictionary
from edc_data_manager.post_migrate_signals import update_query_rule_handlers

from .system_checks import edc_check

style = color_style()


class AppConfig(DjangoAppConfig):
    """AppConfig class for main EDC apps.py.

    Should be the last app in INSTALLED_APPS

    This class is required and may only be used for one
    main project app. For example, `meta_edc`, `intecomm_edc`...

    The post_migrate signal(s) registered here will
    find site globals fully populated.

    For example,
    'post_migrate_user_groups_and_roles' needs site_consents
    to be fully populated before running.
    """

    name = "edc_appconfig"
    verbose_name = "Edc AppConfig"
    has_exportable_data = False
    include_in_administration_section = False

    def ready(self):
        sys.stdout.write(style.MIGRATE_HEADING("Loading edc_appconfig:\n"))
        register(edc_check)

        post_migrate.connect(update_action_types, sender=self)
        site_action_items.create_or_update_action_types()

        post_migrate.connect(update_query_rule_handlers, sender=self)

        post_migrate.connect(post_migrate_user_groups_and_roles, sender=self)

        post_migrate.connect(populate_data_dictionary, sender=self)

    def get_edc_app_name(self):
        """Called in  system checks to confirm this class is used."""
        return self.edc_app_name
