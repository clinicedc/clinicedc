from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Permission, User
from django.shortcuts import get_object_or_404
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_consent.site_consents import AlreadyRegistered
from edc_consent.tests.consent_test_utils import consent_definition_factory
from edc_data_manager.models import DataQuery
from edc_metadata.models import CrfMetadata
from edc_sites.utils import get_site_model_cls
from edc_test_utils.get_user_for_tests import get_user_for_tests
from edc_utils import get_utcnow
from edc_visit_schedule.models import VisitSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from visit_schedule_app.models import SubjectConsent
from visit_schedule_app.visit_schedule import visit_schedule

from edc_subject_dashboard.view_utils import NextDashboardUrl, Perms, QueryButton
from edc_subject_dashboard.view_utils.dashboard_model_button import DashboardModelButton


class TestDataclasses(TestCase):
    @classmethod
    def setUpTestData(cls):
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        VisitSchedule.objects.update(active=False)
        site_visit_schedules.to_model(VisitSchedule)
        for schedule in visit_schedule.schedules.values():
            try:
                consent_definition_factory(model=schedule.consent_model)
            except AlreadyRegistered:
                pass

        cls.user = get_user_for_tests()
        cls.site = get_site_model_cls().objects.get_current()

    def setUp(self):
        self.subject_identifier = "1234567"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "visit_schedule_app.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            report_datetime=self.appointment.appt_datetime,
            visit_code=self.appointment.visit_code,
            visit_code_sequence=self.appointment.visit_code_sequence,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            reason=SCHEDULED,
        )

    def test_button(self):
        # no crf model instance and no perms
        model_obj = CrfMetadata.objects.all()[0]
        btn = DashboardModelButton(
            metadata_model_obj=model_obj, user=self.user, appointment=self.appointment
        )
        self.assertEqual(btn.label, "View")
        self.assertEqual(btn.btn_color, "btn-default")
        self.assertEqual(btn.fa_icon, "fas fa-eye")

        # add instance but no perms
        crf = model_obj.model_cls.objects.create(subject_visit=self.subject_visit)
        model_obj.refresh_from_db()
        btn = DashboardModelButton(
            metadata_model_obj=model_obj, user=self.user, appointment=self.appointment
        )
        self.assertEqual(btn.label, "View")
        self.assertEqual(btn.btn_color, "btn-default")
        self.assertEqual(btn.fa_icon, "fas fa-eye")

        # add view perm
        codename = get_permission_codename("view", model_obj._meta)
        perm = Permission.objects.get(codename=codename)
        self.user.user_permissions.add(perm)
        self.user = get_object_or_404(User, pk=self.user.id)
        self.assertTrue(self.user.has_perm(f"{model_obj._meta.app_label}.{codename}"))

        btn = DashboardModelButton(
            metadata_model_obj=model_obj, user=self.user, appointment=self.appointment
        )
        self.assertEqual(btn.label, "View")
        self.assertEqual(btn.btn_color, "btn-default")
        self.assertEqual(btn.fa_icon, "fas fa-eye")

        # add "add/change" perm
        for action in ["add", "change"]:
            codename = get_permission_codename(action, model_obj._meta)
            perm = Permission.objects.get(codename=codename)
            self.user.user_permissions.add(perm)
        self.user = get_object_or_404(User, pk=self.user.id)

        btn = DashboardModelButton(
            metadata_model_obj=model_obj, user=self.user, appointment=self.appointment
        )
        self.assertEqual(btn.label, "Change")
        self.assertEqual(btn.btn_color, "btn-success")
        self.assertEqual(btn.fa_icon, "fas fa-pen")

        crf.delete()
        btn = DashboardModelButton(
            metadata_model_obj=model_obj, user=self.user, appointment=self.appointment
        )
        self.assertEqual(btn.label, "Add")
        self.assertEqual(btn.btn_color, "btn-warning")
        self.assertEqual(btn.fa_icon, "fas fa-plus")

    def test_perm(self):
        model_obj = CrfMetadata.objects.all()[0]
        perms = Perms(model_obj=model_obj, user=self.user)
        self.assertFalse(perms.add)
        self.assertFalse(perms.change)
        self.assertFalse(perms.view_only)

        # add "add/change" perm
        for action in ["add", "change", "view"]:
            codename = get_permission_codename(action, model_obj._meta)
            perm = Permission.objects.get(codename=codename)
            self.user.user_permissions.add(perm)
        self.user = get_object_or_404(User, pk=self.user.id)

        perms = Perms(model_obj=model_obj, user=self.user)
        self.assertTrue(perms.add)
        self.assertTrue(perms.change)
        self.assertTrue(perms.view)
        self.assertFalse(perms.view_only)

    def test_query_button(self):
        model_obj = CrfMetadata.objects.all()[0]
        btn = QueryButton(model_obj=model_obj, user=self.user, appointment=self.appointment)
        self.assertFalse(btn.show_button)
        self.assertIsNone(btn.url)

        for action in ["add"]:
            codename = get_permission_codename(action, DataQuery._meta)
            perm = Permission.objects.get(codename=codename)
            self.user.user_permissions.add(perm)
        self.user = get_object_or_404(User, pk=self.user.id)
        btn = QueryButton(model_obj=model_obj, user=self.user, appointment=self.appointment)
        self.assertTrue(btn.show_button)
        self.assertIsNotNone(btn.url)

        qs = urlparse(btn.url).query
        self.assertEqual(
            list(parse_qs(qs, keep_blank_values=True).keys()),
            [
                "registered_subject",
                "sender",
                "visit_schedule",
                "visit_code_sequence",
                "title",
            ],
        )
        for v in parse_qs(qs, keep_blank_values=True).values():
            self.assertTrue(v[0])

    def test_next_querystring(self):
        example_log_id = uuid4()
        dashboard_url = NextDashboardUrl(
            dashboard_url_name="listboard_url",
            reverse_kwargs=dict(example_identifier="12345", example_log=example_log_id),
            test_url=False,
        )

        self.assertEqual(
            dashboard_url.querystring,
            (
                "next=edc_model_wrapper:listboard_url,example_identifier,example_log"
                f"&example_identifier=12345&example_log={str(example_log_id)}"
            ),
        )
