import sys

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.sites.management import create_default_site
from django.core.checks import register
from django.core.management.color import color_style
from django.db.models.signals import post_migrate
from multisite.apps import post_migrate_sync_alias

from edc_action_item.post_migrate_signals import update_action_types
from edc_action_item.site_action_items import site_action_items
from edc_action_item.system_checks import edc_action_item_checks
from edc_auth.post_migrate_signals import post_migrate_user_groups_and_roles
from edc_auth.site_auths import site_auths
from edc_consent.site_consents import site_consents
from edc_data_manager.post_migrate_signals import (
    populate_data_dictionary,
    update_query_rule_handlers,
)
from edc_data_manager.site_data_manager import site_data_manager
from edc_export.system_checks import edc_export_checks
from edc_facility.system_checks import holiday_country_check, holiday_path_check
from edc_form_runners.site import site_form_runners
from edc_lab.post_migrate_signals import update_panels_on_post_migrate
from edc_lab.site_labs import site_labs
from edc_list_data.post_migrate_signals import post_migrate_list_data
from edc_list_data.site_list_data import site_list_data
from edc_metadata.metadata_rules import site_metadata_rules
from edc_metadata.system_checks import check_for_metadata_rules
from edc_navbar.site_navbars import site_navbars
from edc_navbar.system_checks import edc_navbar_checks
from edc_notification.post_migrate_signals import post_migrate_update_notifications
from edc_notification.site_notifications import site_notifications
from edc_pdutils.site_values_mappings import site_values_mappings
from edc_prn.site_prn_forms import site_prn_forms
from edc_pylabels.site_label_configs import site_label_configs
from edc_randomization.site_randomizers import site_randomizers
from edc_reportable.post_migrate_signals import post_migrate_load_reference_ranges
from edc_sites.post_migrate_signals import post_migrate_update_sites
from edc_sites.site import sites as site_sites
from edc_sites.system_checks import sites_check
from edc_visit_schedule.post_migrate_signals import populate_visit_schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.system_checks import (
    check_form_collections,
    check_onschedule_exists_in_subject_schedule_history,
    check_subject_schedule_history,
    visit_schedule_check,
)

installed_apps = [x.split(".apps")[0] for x in settings.INSTALLED_APPS]

style = color_style()

__all__ = ["AppConfig"]


class AppConfig(DjangoAppConfig):
    """AppConfig class for main EDC apps.py.

    Should be the last app in INSTALLED_APPS

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
        sys.stdout.write("Loading edc_appconfig ...\n")
        self.call_autodiscovers()
        self.register_system_checks()
        self.unregister_post_migrate_signals()
        self.register_post_migrate_signals()
        sys.stdout.write("Done loading edc_appconfig.\n")

    @staticmethod
    def call_autodiscovers():
        """Call autodiscover on apps to load globals"""
        opts = dict(
            edc_consent=site_consents.autodiscover,
            edc_auth=site_auths.autodiscover,
            edc_sites=site_sites.autodiscover,
            edc_lab=site_labs.autodiscover,
            edc_list_data=site_list_data.autodiscover,
            edc_action_item=site_action_items.autodiscover,
            edc_data_manager=site_data_manager.autodiscover,
            edc_notification=site_notifications.autodiscover,
            edc_form_runners=site_form_runners.autodiscover,
            edc_metadata=site_metadata_rules.autodiscover,
            edc_visit_schedule=site_visit_schedules.autodiscover,
            edc_navbar=site_navbars.autodiscover,
            edc_pdutils=site_values_mappings.autodiscover,
            edc_prn=site_prn_forms.autodiscover,
            edc_randomization=site_randomizers.autodiscover,
            edc_pylabels=site_label_configs.autodiscover,
        )
        # site_offline_models.autodiscover()
        opts = {k: v for k, v in opts.items() if k in installed_apps}
        for app, autodiscover in opts.items():
            autodiscover()

    @staticmethod
    def register_system_checks():
        """Register system checks"""
        from edc_consent.system_checks import check_consents  # wait, app not ready

        sys.stdout.write(" * registering system checks\n")
        if "edc_visit_schedule" in installed_apps:
            sys.stdout.write("   - visit_schedule_check\n")
            register(visit_schedule_check)
            sys.stdout.write("   - check_form_collections\n")
            register(check_form_collections)
            sys.stdout.write("   - check subject schedule history\n")
            register(check_subject_schedule_history, deploy=True)
            sys.stdout.write("   - check onschedule with subject schedule history\n")
            register(check_onschedule_exists_in_subject_schedule_history)
        if "edc_action_item" in installed_apps:
            sys.stdout.write("   - edc_action_item_checks\n")
            register(edc_action_item_checks)
        if "edc_sites" in installed_apps:
            sys.stdout.write("   - sites_check\n")
            register(sites_check)
        if "edc_export" in installed_apps:
            sys.stdout.write("   - edc_export_checks\n")
            register(edc_export_checks, deploy=True)
        if "edc_facility" in installed_apps:
            sys.stdout.write("   - holiday_path_check (deploy only)\n")
            register(holiday_path_check, deploy=True)
            sys.stdout.write("   - holiday_country_check (deploy only)\n")
            register(holiday_country_check, deploy=True)
        if "edc_metadata" in installed_apps:
            sys.stdout.write("   - check_for_metadata_rules (deploy only)\n")
            register(check_for_metadata_rules)
        if "edc_consent" in installed_apps:
            sys.stdout.write("   - check_site_consents\n")
            register(check_consents)
        if "edc_navbar" in installed_apps:
            sys.stdout.write("   - edc_navbar_checks\n")
            register(edc_navbar_checks)

    def unregister_post_migrate_signals(self):
        """Unregister post-migrate signals.

        Unregister the default signal that creates "example.com"
        instead of deleting the site instance later.
        Deleting the "example.com" site instance later raises an
        OperationalError("cannot modify your_model because it is a
        view"). The exception is refering to any unmanaged model
        (your_model) based on SQL VIEWS that has a FK to model Sites.

        See also: edc_qareports.models.dbviews
        """
        if not getattr(settings, "EDC_SITES_CREATE_DEFAULT", True):
            sys.stdout.write(
                " * unregistering django post-migrate signal `create_default_site` ...\n"
            )
            post_migrate.disconnect(
                create_default_site, sender=django_apps.get_app_config("sites")
            )

    def register_post_migrate_signals(self):
        """Register post-migrate signals."""
        sys.stdout.write(" * registering post-migrate signals ...\n")
        if "edc_visit_schedule" in installed_apps:
            sys.stdout.write("   - post_migrate.populate_visit_schedule\n")
            post_migrate.connect(
                populate_visit_schedule,
                sender=self,
                dispatch_uid="edc_visit_schedule.populate_visit_schedule",
            )
        if "edc_sites" in installed_apps:
            sys.stdout.write("   - post_migrate.post_migrate_update_sites\n")
            post_migrate.connect(
                post_migrate_update_sites,
                sender=self,
                dispatch_uid="edc_sites.post_migrate_update_sites",
            )
        if "multisite" in installed_apps:
            sys.stdout.write("   - post_migrate.multisite.post_migrate_sync_alias\n")
            post_migrate.connect(
                post_migrate_sync_alias,
                sender=self,
                dispatch_uid="multisite.post_migrate_sync_alias",
            )
        if "edc_lab" in installed_apps:
            sys.stdout.write("   - post_migrate.update_panels_on_post_migrate\n")
            post_migrate.connect(
                update_panels_on_post_migrate,
                sender=self,
                dispatch_uid="edc_lab.update_panels_on_post_migrate",
            )
        if "edc_list_data" in installed_apps:
            sys.stdout.write("   - post_migrate.post_migrate_list_data\n")
            post_migrate.connect(
                post_migrate_list_data,
                sender=self,
                dispatch_uid="edc_list_data.post_migrate_list_data",
            )
        if "edc_action_item" in installed_apps:
            sys.stdout.write("   - post_migrate.update_action_types\n")
            post_migrate.connect(
                update_action_types,
                sender=self,
                dispatch_uid="edc_action_item.update_action_types",
            )
        if "edc_auth" in installed_apps:
            sys.stdout.write("   - post_migrate.post_migrate_user_groups_and_roles\n")
            post_migrate.connect(
                post_migrate_user_groups_and_roles,
                sender=self,
                dispatch_uid="edc_auth.post_migrate_user_groups_and_roles",
            )
        if "edc_data_manager" in installed_apps:
            sys.stdout.write("   - post_migrate.update_query_rule_handlers\n")
            post_migrate.connect(
                update_query_rule_handlers,
                sender=self,
                dispatch_uid="edc_data_manager.update_query_rule_handlers",
            )
            sys.stdout.write("   - post_migrate.populate_data_dictionary\n")
            post_migrate.connect(
                populate_data_dictionary,
                sender=self,
                dispatch_uid="edc_data_manager.populate_data_dictionary",
            )
        if "edc_notification" in installed_apps:
            sys.stdout.write("   - post_migrate.post_migrate_update_notifications\n")
            post_migrate.connect(
                post_migrate_update_notifications,
                sender=self,
                dispatch_uid="edc_notification.post_migrate_update_notifications",
            )
        if "edc_reportable" in installed_apps:
            sys.stdout.write("   - post_migrate.post_migrate_load_reference_ranges\n")
            post_migrate.connect(
                post_migrate_load_reference_ranges,
                sender=self,
                dispatch_uid="edc_reportable.post_migrate_load_reference_ranges",
            )
