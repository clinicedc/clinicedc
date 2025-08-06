from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils import get_utcnow

from edc_consent.consent_definition import ConsentDefinition
from edc_consent.exceptions import SiteConsentError
from edc_consent.site_consents import site_consents


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestConsentModel(TestCase):
    def setUp(self):
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        site_consents.registry = {}

    def default_options(self, **kwargs):
        options = dict(
            start=self.study_open_datetime,
            end=self.study_close_datetime,
            gender=["M", "F"],
            version="1",
            age_min=16,
            age_max=64,
            age_is_adult=18,
        )
        options.update(**kwargs)
        return options

    def test_ok(self):
        ConsentDefinition("consent_app.subjectconsentv1", **self.default_options())

    def test_cdef_name(self):
        cdef1 = ConsentDefinition("consent_app.subjectconsentv1", **self.default_options())
        self.assertEqual(cdef1.name, "consent_app.subjectconsentv1-1")
        site_consents.register(cdef1)
        site_consents.get_consent_definition("consent_app.subjectconsentv1")
        site_consents.get_consent_definition(model="consent_app.subjectconsentv1")
        site_consents.get_consent_definition(version="1")

        # add country
        site_consents.registry = {}
        cdef1 = ConsentDefinition(
            "consent_app.subjectconsentugv1", **self.default_options(country="uganda")
        )
        self.assertEqual(cdef1.name, "consent_app.subjectconsentugv1-1")
        site_consents.register(cdef1)
        cdef2 = site_consents.get_consent_definition(country="uganda")
        self.assertEqual(cdef1, cdef2)

    def test_with_country(self):
        site_consents.registry = {}
        cdef1 = ConsentDefinition(
            "consent_app.subjectconsentv1", country="uganda", **self.default_options()
        )
        site_consents.register(cdef1)
        cdef2 = site_consents.get_consent_definition(country="uganda")
        self.assertEqual(cdef1, cdef2)

    def test_with_country_raises_on_potential_duplicate(self):
        site_consents.registry = {}
        cdef1 = ConsentDefinition(
            "consent_app.subjectconsentv1", country="uganda", **self.default_options()
        )
        cdef2 = ConsentDefinition(
            "consent_app.subjectconsentugv1", country="uganda", **self.default_options()
        )
        site_consents.register(cdef1)
        site_consents.register(cdef2)
        self.assertRaises(
            SiteConsentError, site_consents.get_consent_definition, country="uganda"
        )

    def test_duplicate_version(self):
        site_consents.registry = {}
        cdef1 = ConsentDefinition(
            "consent_app.subjectconsentv1", country="uganda", **self.default_options()
        )
        cdef2 = ConsentDefinition(
            "consent_app.subjectconsentugv1", country="uganda", **self.default_options()
        )
        site_consents.register(cdef1)
        site_consents.register(cdef2)
        self.assertRaises(
            SiteConsentError, site_consents.get_consent_definition, country="uganda"
        )
