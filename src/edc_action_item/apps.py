from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = 'edc_action_item'
    verbose_name = 'Action Items'
    has_exportable_data = True

    def ready(self):
        from .signals import action_on_post_delete
        from .signals import update_or_create_action_item_on_post_save
        from .signals import send_email_on_new_action_item_post_save
        pass
