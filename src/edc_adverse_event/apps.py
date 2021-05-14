from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_adverse_event"
    verbose_name = "Edc Adverse Events"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        from .signals import post_delete_ae_susar  # noqa; noqa
        from .signals import update_ae_initial_for_susar  # noqa
        from .signals import update_ae_initial_susar_reported  # noqa
        from .signals import update_ae_notifications_for_tmg_group  # noqa
        from .signals import update_death_notifications_for_tmg_group  # noqa
