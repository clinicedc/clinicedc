import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks.registry import register
from django.core.management.color import color_style
from django.db.models.signals import post_migrate
from edc_action_item import site_action_items
from edc_action_item.post_migrate_signals import update_action_types
from edc_auth.post_migrate_signals import post_migrate_user_groups_and_roles
from edc_data_manager.post_migrate_signals import (
    populate_data_dictionary,
    update_query_rule_handlers,
)

from .system_checks import edc_check

style = color_style()


class EdcAppConfig(DjangoAppConfig):

    """AppConfig class for main EDC apps.py.

    This class is required and may only be used for one
    main project app. For example, `meta_edc`, `intecomm_edc`...

    The post_migrate signal(s) registered here will
    find site globals fully populated. For example,
    'post_migrate_user_groups_and_roles' needs site_consents
    to be fully populated before running.
    """

    edc_app_name: str = settings.EDC_APP_NAME

    def ready(self):
        sys.stdout.write(style.ERROR(f"\nDefault EDC app is '{self.edc_app_name}'. \n\n"))
        register(edc_check)
        post_migrate.connect(update_action_types, sender=self)
        site_action_items.create_or_update_action_types()

        post_migrate.connect(populate_data_dictionary, sender=self)
        post_migrate.connect(update_query_rule_handlers, sender=self)
        post_migrate.connect(post_migrate_user_groups_and_roles, sender=self)

    def get_edc_app_name(self):
        """Called in  system checks to confirm this class is used."""
        return self.edc_app_name
