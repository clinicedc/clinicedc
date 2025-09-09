from datetime import datetime
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase

from edc_consent.consent_definition import ConsentDefinition
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from tests.consents import consent_v1
from tests.sites import all_sites
from tests.visit_schedules.visit_schedule_action_item import get_visit_schedule


class TestCaseMixin(TestCase):

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    @staticmethod
    def enroll(
        site_id: int | None = None,
        consent_datetime: datetime | None = None,
        cdef: ConsentDefinition | None = None,
    ):
        site = Site.objects.get(id=site_id or settings.SITE_ID)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(get_visit_schedule(cdef or consent_v1))

        site_consents.registry = {}
        site_consents.register(cdef or consent_v1)
        consent_datetime = consent_datetime or get_utcnow()
        cdef = site_consents.get_consent_definition(report_datetime=consent_datetime)
        identity = str(uuid4())
        subject_consent = cdef.model_create(
            consent_datetime=consent_datetime,
            dob=consent_datetime - relativedelta(years=25),
            site=site,
            identity=identity,
            confirm_identity=identity,
        )
        schedule = site_visit_schedules.get_visit_schedule(
            "visit_schedule_action_item"
        ).schedules.get("schedule_action_item")
        schedule.put_on_schedule(
            subject_consent.subject_identifier,
            subject_consent.consent_datetime,
            skip_get_current_site=True,
        )
        return subject_consent.subject_identifier

    @staticmethod
    def fake_enroll(
        subject_identifier: str | None = None,
        site_id: int | None = None,
        site: Site | None = None,
    ) -> str:
        opts = dict(subject_identifier=subject_identifier or str(uuid4()))
        if site:
            opts["site"] = site
        else:
            opts.update(site_id=site_id)
        rs = RegisteredSubject.objects.create(**opts)
        return rs.subject_identifier
