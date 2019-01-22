import sys

from django.apps import AppConfig as DjangoApponfig

from .site_action_items import site_action_items


class AppConfig(DjangoApponfig):
    name = "edc_action_item"
    verbose_name = "Action Items"
    has_exportable_data = True

    def ready(self):
        from .signals import action_on_post_delete
        from .signals import action_item_notification_on_post_create_historical_record
        from .signals import update_or_create_action_item_on_post_save

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_action_items.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
