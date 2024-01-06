import sys

from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_consent"
    verbose_name = "Edc Consent"
    include_in_administration_section = True

    def ready(self):
        from .site_consents import site_consents

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_consents.autodiscover()
        for cdef in site_consents.registry.values():
            start = cdef.start.strftime("%Y-%m-%d %Z")
            end = cdef.end.strftime("%Y-%m-%d %Z")
            sys.stdout.write(f" * {cdef.name} valid {start} to {end}\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
