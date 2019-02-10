from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag

from ..consent import Consent
from ..site_consents import site_consents


class ConsentTestCase(TestCase):
    def setUp(self):
        super().setUp()
        site_consents.registry = {}
        self.dob = self.study_open_datetime - relativedelta(years=25)

    def consent_object_factory(
        self,
        model=None,
        start=None,
        end=None,
        gender=None,
        updates_versions=None,
        version=None,
        age_min=None,
        age_max=None,
        age_is_adult=None,
    ):
        options = dict(
            start=start or self.study_open_datetime,
            end=end or self.study_close_datetime,
            gender=gender or ["M", "F"],
            updates_versions=updates_versions or [],
            version=version or "1",
            age_min=age_min or 16,
            age_max=age_max or 64,
            age_is_adult=age_is_adult or 18,
        )
        model = model or "edc_consent.subjectconsent"
        consent = Consent(model, **options)
        site_consents.register(consent)
        return consent
