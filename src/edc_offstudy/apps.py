from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_offstudy'
    verbose_name = 'Edc Off-study'

    def ready(self):
        from edc_offstudy.signals import off_study_post_save
