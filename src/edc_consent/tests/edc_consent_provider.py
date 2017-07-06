import string

from dateutil.relativedelta import relativedelta
from faker.providers import BaseProvider
from random import choice
from django.apps import apps as django_apps
from edc_constants.constants import FEMALE, MALE
from edc_protocol.tests import get_utcnow

from ..site_consents import site_consents


class EdcConsentProvider(BaseProvider):

    @property
    def consent_model(self):
        return django_apps.get_app_config('edc_base_test').consent_model

    def gender(self):
        return choice([FEMALE, MALE])

    def initials(self):
        return choice(list(string.ascii_uppercase)) + choice(list(string.ascii_uppercase))

    def dob_for_consenting_adult(self):
        consent = site_consents.get_consent(
            consent_model=self.consent_model,
            report_datetime=get_utcnow())
        years = choice(range(consent.age_is_adult, consent.age_max + 1))
        return (get_utcnow() - relativedelta(years=years)).date()

    def dob_for_consenting_minor(self):
        consent = site_consents.get_consent(
            self.consent_model, report_datetime=get_utcnow())
        years = choice(range(consent.age_min, consent.age_is_adult + 1) - 1)
        return (get_utcnow() - relativedelta(years=years)).date()

    def age_for_consenting_adult(self):
        consent = site_consents.get_consent(
            consent_model=self.consent_model, report_datetime=get_utcnow())
        return choice(range(consent.age_is_adult, consent.age_max + 1))

    def age_for_consenting_minor(self):
        consent = site_consents.get_consent(
            consent_model=self.consent_model, report_datetime=get_utcnow())
        return choice(range(consent.age_min, consent.age_is_adult + 1) - 1)

    def yesterday(self):
        return get_utcnow() - relativedelta(days=1)

    def last_week(self):
        return get_utcnow() - relativedelta(weeks=1)

    def last_month(self):
        return get_utcnow() - relativedelta(months=1)

    def two_months_ago(self):
        return get_utcnow() - relativedelta(months=2)

    def three_months_ago(self):
        return get_utcnow() - relativedelta(months=3)

    def six_months_ago(self):
        return get_utcnow() - relativedelta(months=6)

    def twelve_months_ago(self):
        return get_utcnow() - relativedelta(months=12)
