from django.apps import AppConfig as DjangoApponfig

from .site_action_items import site_action_items


class AppConfig(DjangoApponfig):
    name = 'edc_action_item'
    verbose_name = 'Action Items'

    def ready(self):
        from .signals import (action_item_on_post_save,
                              update_action_item_on_post_save)
        # site_action_items.autodiscover()
