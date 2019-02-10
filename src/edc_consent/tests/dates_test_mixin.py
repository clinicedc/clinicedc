import copy
import sys

from copy import deepcopy
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.management.color import color_style

from ..site_consents import site_consents


class DatesTestMixin:

    """A mixin for tests that changes the protocol start and
    end dates to be in the past.

    Also changes the consent periods for all registered
    consents relative to the changed study open/close dates.

    Use get_utcnow to return the study open date.
    """

    study_tdelta = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site_consents_registry = {}
        style = color_style()
        sys.stdout.write(
            style.NOTICE(
                "\n{}. Overwriting study open/close and consent.start/end dates "
                "for tests only.\n".format(cls.__name__)
            )
        )
        study_open_datetime = django_apps.app_configs[
            "edc_protocol"
        ].study_open_datetime
        study_close_datetime = django_apps.app_configs[
            "edc_protocol"
        ].study_close_datetime
        django_apps.app_configs[
            "edc_protocol"
        ]._original_study_open_datetime = study_open_datetime
        django_apps.app_configs[
            "edc_protocol"
        ]._original_study_close_datetime = study_close_datetime

        ropen = django_apps.app_configs["edc_protocol"].arrow.ropen
        rclose = django_apps.app_configs["edc_protocol"].arrow.rclose

        cls.study_tdelta = rclose.floor("hour").datetime - ropen.floor("hour").datetime

        django_apps.app_configs["edc_protocol"].study_open_datetime = (
            ropen.datetime - relativedelta(days=cls.study_tdelta.days)
        )
        django_apps.app_configs["edc_protocol"].study_close_datetime = ropen.ceil(
            "hour"
        ).datetime

        edc_protocol_app_config = django_apps.get_app_config("edc_protocol")
        study_open_datetime = edc_protocol_app_config.study_open_datetime
        study_close_datetime = edc_protocol_app_config.study_close_datetime
        sys.stdout.write(
            style.NOTICE(
                " * test study open datetime: {}\n".format(study_open_datetime)
            )
        )
        sys.stdout.write(
            style.NOTICE(
                " * test study close datetime: {}\n".format(study_close_datetime)
            )
        )

        testconsents = []
        if site_consents.consents:
            new_startdate = site_consents.consents[0].arrow.rstart.floor(
                "hour"
            ).datetime - relativedelta(days=cls.study_tdelta.days)
            tdelta = (
                site_consents.consents[0].arrow.rstart.floor("hour").datetime
                - new_startdate
            )

            for consent in site_consents.consents:
                test_consent = copy.copy(consent)
                test_consent.start = test_consent.arrow.rstart.floor(
                    "hour"
                ).datetime - relativedelta(days=tdelta.days)
                test_consent.end = test_consent.arrow.rend.ceil(
                    "hour"
                ).datetime - relativedelta(days=tdelta.days)
                sys.stdout.write(
                    style.NOTICE(
                        " * {}: {} - {}\n".format(
                            test_consent.name, test_consent.start, test_consent.end
                        )
                    )
                )
                testconsents.append(test_consent)
            cls.site_consents_registry = deepcopy(site_consents.registry)
            for test_consent in testconsents:
                site_consents.register(test_consent)

    @classmethod
    def tearDownClass(cls):
        """Restores edc_protocol app_config open/close dates
        and edc_consent site_consents registry.
        """
        super().tearDownClass()
        style = color_style()
        study_open_datetime = django_apps.app_configs[
            "edc_protocol"
        ]._original_study_open_datetime
        study_close_datetime = django_apps.app_configs[
            "edc_protocol"
        ]._original_study_close_datetime
        django_apps.app_configs[
            "edc_protocol"
        ].study_open_datetime = study_open_datetime
        django_apps.app_configs[
            "edc_protocol"
        ].study_close_datetime = study_close_datetime
        site_consents.registry = cls.site_consents_registry
        sys.stdout.write(style.NOTICE("\n * restored original values\n"))

    def get_utcnow(self):
        """Returns the earliest date allowed.
        """
        return self.study_open_datetime

    @property
    def study_open_datetime(self):
        edc_protocol_app_config = django_apps.get_app_config("edc_protocol")
        return edc_protocol_app_config.study_open_datetime

    @property
    def study_close_datetime(self):
        edc_protocol_app_config = django_apps.get_app_config("edc_protocol")
        return edc_protocol_app_config.study_close_datetime
