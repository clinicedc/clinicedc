from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.consents import consent_v1
from clinicedc_tests.helper import Helper
from clinicedc_tests.models import SubjectScreening
from clinicedc_tests.visit_schedules.visit_schedule import get_visit_schedule
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings, tag
from django.utils import timezone

from edc_consent import site_consents
from edc_refusal.forms import SubjectRefusalForm
from edc_refusal.models import RefusalReasons, SubjectRefusal
from edc_refusal.utils import get_subject_refusal_model, get_subject_refusal_model_cls
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


@tag("refusal")
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC")))
@override_settings(SITE_ID=10)
class TestForms(TestCase):
    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule = get_visit_schedule(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )
        self.subject_identifier = subject_consent.subject_identifier
        self.subject_screening = SubjectScreening.objects.all()[0]

    def get_data(self):
        refusal_reason = RefusalReasons.objects.all()[0]
        return {
            "screening_identifier": self.subject_screening.screening_identifier,
            "report_datetime": timezone.now(),
            "reason": refusal_reason,
            "other_reason": None,
            "comment": None,
            "site": Site.objects.get(id=settings.SITE_ID),
        }

    @override_settings(SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal")
    def test_model_funcs(self):
        self.assertEqual(get_subject_refusal_model(), "edc_refusal.subjectrefusal")
        self.assertEqual(get_subject_refusal_model_cls(), SubjectRefusal)

    @override_settings(SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal")
    def test_subject_refusal_ok(self):
        form = SubjectRefusalForm(data=self.get_data(), instance=None)
        form.is_valid()
        self.assertEqual(form._errors, {})
        form.save()
        self.assertEqual(SubjectRefusal.objects.all().count(), 1)

    @override_settings(SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal")
    def test_add_subject_refusal_set_subject_screening_refused_true(self):
        self.assertFalse(self.subject_screening.refused)

        form = SubjectRefusalForm(data=self.get_data(), instance=None)
        form.save()
        self.subject_screening.refresh_from_db()
        self.assertTrue(self.subject_screening.refused)

    @override_settings(SUBJECT_REFUSAL_MODEL="edc_refusal.subjectrefusal")
    def test_delete_subject_refusal_sets_subject_screening_refused_false(self):
        self.assertFalse(self.subject_screening.refused)

        form = SubjectRefusalForm(data=self.get_data(), instance=None)
        form.save()
        self.subject_screening.refresh_from_db()
        self.assertTrue(self.subject_screening.refused)

        subject_refusal = SubjectRefusal.objects.get(
            screening_identifier=self.subject_screening.screening_identifier
        )
        subject_refusal.delete()
        self.subject_screening.refresh_from_db()
        self.assertFalse(self.subject_screening.refused)
