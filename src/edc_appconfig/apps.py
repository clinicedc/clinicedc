import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django.db.models.signals import post_migrate

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
        from edc_action_item.post_migrate_signals import update_action_types
        from edc_auth.post_migrate_signals import post_migrate_user_groups_and_roles
        from edc_data_manager.post_migrate_signals import (
            populate_data_dictionary,
            update_query_rule_handlers,
        )
        from edc_lab.post_migrate_signals import update_panels_on_post_migrate
        from edc_list_data.post_migrate_signals import post_migrate_list_data
        from edc_notification.post_migrate_signals import (
            post_migrate_update_notifications,
        )
        from edc_sites.post_migrate_signals import post_migrate_update_sites
        from edc_visit_schedule.post_migrate_signals import populate_visit_schedule

        sys.stdout.write("Loading edc_appconfig ...\n")

        sys.stdout.write("  * post_migrate.populate_visit_schedule\n")
        post_migrate.connect(populate_visit_schedule, sender=self)
        sys.stdout.write("  * post_migrate.post_migrate_update_sites\n")
        post_migrate.connect(post_migrate_update_sites, sender=self)
        sys.stdout.write("  * post_migrate.update_panels_on_post_migrate\n")
        post_migrate.connect(update_panels_on_post_migrate, sender=self)
        sys.stdout.write("  * post_migrate.post_migrate_list_data\n")
        post_migrate.connect(post_migrate_list_data, sender=self)
        sys.stdout.write("  * post_migrate.update_action_types\n")
        post_migrate.connect(update_action_types, sender=self)
        sys.stdout.write("  * post_migrate.post_migrate_user_groups_and_roles\n")
        post_migrate.connect(post_migrate_user_groups_and_roles, sender=self)
        sys.stdout.write("  * post_migrate.update_query_rule_handlers\n")
        post_migrate.connect(update_query_rule_handlers, sender=self)
        sys.stdout.write("  * post_migrate.populate_data_dictionary\n")
        post_migrate.connect(populate_data_dictionary, sender=self)
        sys.stdout.write("  * post_migrate.post_migrate_update_notifications\n")
        post_migrate.connect(post_migrate_update_notifications, sender=self)

        sys.stdout.write("  Done\n")
