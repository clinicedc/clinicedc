import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .site_list_data import site_list_data, SiteListDataError


style = color_style()


"""
If you need list data in your tests add to your test case:

    @classmethod
    def setUpClass(cls):
        site_list_data.autodiscover()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

"""


class AppConfig(DjangoAppConfig):
    name = "edc_list_data"
    verbose_name = "Edc List Data"

    def ready(self):

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        if "test" in sys.argv or "runtests.py" in sys.argv:
            sys.stdout.write(
                style.WARNING(
                    f" Not updating list data for tests. "
                    "Add site_list_data.autodiscover() to your test setUp.\n"
                )
            )
        elif "migrate" in sys.argv or "makemigrations" in sys.argv:
            pass
        else:
            try:
                site_list_data.autodiscover()
            except SiteListDataError as e:
                sys.stdout.write(
                    style.ERROR(
                        f' Failed to update list data! Fix the issue and restart. \n "{e}".\n'
                    )
                )
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
