from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_dashboard'

    most_recent_models = {
        'subject': 'edc_example.subjectconsent',
    }

    search_models = {
        'subject': ('edc_example.subjectconsent', 'subject_identifier'),
    }
