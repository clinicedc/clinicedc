from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.visit_schedules.visit_schedule_metadata.visit_schedule import (
    get_visit_schedule,
)
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, override_settings, tag
from django.test.client import RequestFactory

from edc_consent import site_consents
from edc_facility.import_holidays import import_holidays
from edc_lab.models.panel import Panel
from edc_metadata.constants import REQUIRED
from edc_metadata.models import (
    CrfMetadata,
    CrfMetadataMissing,
    DataMissingReason,
)
from edc_metadata.views import ManageMissingFlagUnFlagView
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestManageMissingFlagUnFlagView(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        self.user = User.objects.create(username="erik")
        for name in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]:
            Panel.objects.create(name=name)
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        self.subject_visit = helper.enroll_to_baseline(
            visit_schedule_name=visit_schedule.name, schedule_name="schedule"
        )
        self.appointment = self.subject_visit.appointment
        self.sid = self.subject_visit.subject_identifier
        self.opts = dict(
            subject_identifier=self.sid,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            visit_code=self.appointment.visit_code,
        )
        self.reason = DataMissingReason.objects.create(
            name="test_reason", display_name="Test reason"
        )

    def _flag(self, crf):
        return CrfMetadataMissing.objects.create(
            subject_identifier=crf.subject_identifier,
            visit_schedule_name=crf.visit_schedule_name,
            schedule_name=crf.schedule_name,
            visit_code=crf.visit_code,
            visit_code_sequence=crf.visit_code_sequence,
            model=crf.model,
            reason=self.reason,
            site_id=10,
        )

    def _first_crf(self):
        return CrfMetadata.objects.filter(
            entry_status=REQUIRED, site_id=10, **self.opts
        ).first()

    def _post_view(self, data, allowed=(10,)):
        view = ManageMissingFlagUnFlagView()
        view.kwargs = dict(self.opts)
        view.allowed_site_ids = lambda: list(allowed)
        view.can_flag = lambda *_: True
        request = RequestFactory().post("/", data=data)
        request.user = self.user
        request.session = {}
        request._messages = FallbackStorage(request)
        view.request = request
        return view, request

    # ----------------------------------------------------------------- GET rows
    def test_rows_list_outstanding_with_no_flag(self):
        rows = ManageMissingFlagUnFlagView._rows(
            CrfMetadata, CrfMetadataMissing, "crf", self.opts, [10], panel=False
        )
        expected = CrfMetadata.objects.filter(
            entry_status=REQUIRED, site_id=10, **self.opts
        ).count()
        self.assertEqual(len(rows), expected)
        self.assertTrue(all(r["flag"] is None for r in rows))

    def test_rows_reflect_an_existing_flag(self):
        crf = self._first_crf()
        self._flag(crf)
        rows = ManageMissingFlagUnFlagView._rows(
            CrfMetadata, CrfMetadataMissing, "crf", self.opts, [10], panel=False
        )
        flagged = [r for r in rows if r["flag"] is not None]
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged[0]["meta"].model, crf.model)

    # -------------------------------------------------------------------- POST
    def test_post_flag_creates_row(self):
        crf = self._first_crf()
        view, request = self._post_view(
            dict(
                kind="crf",
                rows="0",
                model_0=crf.model,
                seq_0=crf.visit_code_sequence,
                reason_0=self.reason.id,
                comment_0="no source",
            )
        )
        response = view.post(request)
        self.assertEqual(response.status_code, 302)
        obj = CrfMetadataMissing.objects.get(
            subject_identifier=self.sid, visit_code=crf.visit_code, model=crf.model
        )
        # the posting user is captured (django_audit_fields only does this in admin)
        self.assertEqual(obj.user_created, "erik")
        self.assertEqual(obj.user_modified, "erik")

    def test_post_blank_reason_clears_existing_flag(self):
        crf = self._first_crf()
        self._flag(crf)
        view, request = self._post_view(
            dict(
                kind="crf",
                rows="0",
                model_0=crf.model,
                seq_0=crf.visit_code_sequence,
                reason_0="",  # blank reason -> un-flag
            )
        )
        view.post(request)
        self.assertFalse(
            CrfMetadataMissing.objects.filter(
                subject_identifier=self.sid, visit_code=crf.visit_code, model=crf.model
            ).exists()
        )

    def test_post_flag_denied_for_other_site(self):
        crf = self._first_crf()
        view, request = self._post_view(
            dict(
                kind="crf",
                rows="0",
                model_0=crf.model,
                seq_0=crf.visit_code_sequence,
                reason_0=self.reason.id,
            ),
            allowed=(9999,),  # the source row's site (10) is not allowed
        )
        view.post(request)
        self.assertFalse(
            CrfMetadataMissing.objects.filter(
                subject_identifier=self.sid, model=crf.model
            ).exists()
        )
