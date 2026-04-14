import sys

from django.apps import apps as django_apps
from django.core.management import BaseCommand

from edc_qareports.model_mixins import QaReportModelMixin


class Command(BaseCommand):
    help = (
        "Safely recreate the database view for models declared "
        "with `django_db_views.DBView` to use a local account "
        "as definer."
    )

    def handle(self, *args, **options):  # noqa: ARG002
        for model_cls in django_apps.get_models():
            if issubclass(model_cls, (QaReportModelMixin,)):
                sys.stdout.write(f"{model_cls._meta.db_table}\n")
                try:
                    model_cls.recreate_db_view()
                except AttributeError as e:
                    sys.stdout.write(f"{e}\n")
                except TypeError as e:
                    sys.stdout.write(f"{e}\n")
