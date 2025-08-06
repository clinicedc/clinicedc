from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Permission, User
from django.shortcuts import get_object_or_404
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_data_manager.models import DataQuery
from edc_metadata.models import CrfMetadata
from edc_registration.models import RegisteredSubject
from edc_sites.utils import get_site_model_cls
from edc_subject_dashboard.view_utils import CrfButton
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit

from dashboard_app.consents import consent_v1
from dashboard_app.models import SubjectConsent
from edc_view_utils import DashboardModelButton, Perms, QueryButton

from .test_case_mixin import TestCaseMixin


@override_settings(SITE_ID=110, EDC_SITES_REGISTER_DEFAULT=False)
class TestDataclasses(TestCaseMixin, TestCase):
    def setUp(self):
        site_consents.registry = {}
        site_consents.register(consent_v1)
        self.current_site = get_site_model_cls().objects.get_current()
        self.subject_identifier = "101-1234567-0"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier, consent_datetime=get_utcnow()
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "dashboard_app.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=self.subject_identifier
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
        self.assertEqual(btn.label, "Add")
        self.assertEqual(btn.color, "warning")
        self.assertEqual(btn.fa_icon, "fas fa-plus")
        self.assertEqual(btn.disabled, "disabled")

        btn = CrfButton(
            metadata_model_obj=model_obj, user=self.user, appointment=self.appointment
        )
        self.assertEqual(btn.label, "Add")
        self.assertEqual(btn.color, "warning")
        self.assertEqual(btn.fa_icon, "fas fa-plus")
        self.assertEqual(btn.disabled, "disabled")

        # add instance but no perms
        crf = model_obj.model_cls.objects.create(subject_visit=self.subject_visit)
        model_obj.refresh_from_db()
        btn = DashboardModelButton(
            metadata_model_obj=model_obj, user=self.user, appointment=self.appointment
        )
        self.assertEqual(btn.label, "View")
        self.assertEqual(btn.color, "default")
        self.assertEqual(btn.fa_icon, "fas fa-eye")
        self.assertEqual(btn.disabled, "disabled")

        btn = CrfButton(
            metadata_model_obj=model_obj, user=self.user, appointment=self.appointment
        )
        self.assertEqual(btn.label, "View")
        self.assertEqual(btn.color, "success")
        self.assertEqual(btn.fa_icon, "fas fa-eye")
        self.assertEqual(btn.disabled, "disabled")

        # add view perm
        codename = get_permission_codename("view", crf._meta)
        perm = Permission.objects.get(
            content_type__app_label="dashboard_app", codename=codename
        )
        self.user.user_permissions.add(perm)
        self.user = get_object_or_404(User, pk=self.user.id)
        self.assertTrue(self.user.has_perm(f"{crf._meta.app_label}.{codename}"))

        btn = DashboardModelButton(
            metadata_model_obj=model_obj,
            user=self.user,
            appointment=self.appointment,
            current_site=self.current_site,
        )
        self.assertEqual(btn.label, "View")
        self.assertEqual(btn.color, "default")
        self.assertEqual(btn.fa_icon, "fas fa-eye")
        self.assertEqual(btn.disabled, "")

        btn = CrfButton(
            metadata_model_obj=model_obj,
            user=self.user,
            appointment=self.appointment,
            current_site=self.current_site,
        )
        self.assertEqual(btn.label, "View")
        self.assertEqual(btn.color, "success")
        self.assertEqual(btn.fa_icon, "fas fa-eye")
        self.assertEqual(btn.disabled, "")

        # add "add/change" perm
        for action in ["add", "change"]:
            codename = get_permission_codename(action, crf._meta)
            perm = Permission.objects.get(
                content_type__app_label="dashboard_app", codename=codename
            )

            self.user.user_permissions.add(perm)
        self.user = get_object_or_404(User, pk=self.user.id)

        btn = DashboardModelButton(
            metadata_model_obj=model_obj,
            user=self.user,
            appointment=self.appointment,
            current_site=self.current_site,
        )
        self.assertEqual(btn.label, "Change")
        self.assertEqual(btn.color, "success")
        self.assertEqual(btn.fa_icon, "fas fa-pen")
        self.assertEqual(btn.disabled, "")

        btn = CrfButton(
            metadata_model_obj=model_obj,
            user=self.user,
            appointment=self.appointment,
            current_site=self.current_site,
        )
        self.assertEqual(btn.label, "Change")
        self.assertEqual(btn.color, "success")
        self.assertEqual(btn.fa_icon, "fas fa-pen")
        self.assertEqual(btn.disabled, "")

        crf.delete()
        btn = DashboardModelButton(
            metadata_model_obj=model_obj,
            user=self.user,
            appointment=self.appointment,
            current_site=self.current_site,
        )
        self.assertEqual(btn.label, "Add")
        self.assertEqual(btn.color, "warning")
        self.assertEqual(btn.fa_icon, "fas fa-plus")
        self.assertEqual(btn.disabled, "")

        btn = CrfButton(
            metadata_model_obj=model_obj,
            user=self.user,
            appointment=self.appointment,
            current_site=self.current_site,
        )
        self.assertEqual(btn.label, "Add")
        self.assertEqual(btn.color, "warning")
        self.assertEqual(btn.fa_icon, "fas fa-plus")
        self.assertEqual(btn.disabled, "")

    def test_perm(self):
        model_obj = CrfMetadata.objects.all()[0]
        crf = model_obj.model_cls.objects.create(subject_visit=self.subject_visit)
        perms = Perms(
            model_cls=CrfMetadata,
            user=self.user,
            site=crf.site,
            current_site=self.current_site,
        )
        self.assertFalse(perms.add)
        self.assertFalse(perms.change)
        self.assertFalse(perms.view_only)

        # add "add/change" perm
        for action in ["add", "change", "view"]:
            codename = get_permission_codename(action, CrfMetadata._meta)
            perm = Permission.objects.get(codename=codename)
            self.user.user_permissions.add(perm)
        self.user = get_object_or_404(User, pk=self.user.id)

        perms = Perms(
            model_cls=CrfMetadata,
            user=self.user,
            site=crf.site,
            current_site=self.current_site,
        )
        self.assertTrue(perms.add)
        self.assertTrue(perms.change)
        self.assertTrue(perms.view)
        self.assertFalse(perms.view_only)

    def test_query_button(self):
        model_obj = CrfMetadata.objects.all()[0]
        btn = QueryButton(
            metadata_model_obj=model_obj,
            user=self.user,
            current_site=self.current_site,
            appointment=self.appointment,
            registered_subject=self.registered_subject,
        )
        self.assertEqual(btn.disabled, "disabled")
        self.assertFalse(btn.perms.add)
        self.assertFalse(btn.perms.change)
        self.assertFalse(btn.perms.view)
        self.assertFalse(btn.perms.view_only)

        for action in ["add"]:
            codename = get_permission_codename(action, DataQuery._meta)
            perm = Permission.objects.get(codename=codename)
            self.user.user_permissions.add(perm)
        self.user = get_object_or_404(User, pk=self.user.id)
        btn = QueryButton(
            metadata_model_obj=model_obj,
            user=self.user,
            current_site=self.current_site,
            appointment=self.appointment,
            registered_subject=self.registered_subject,
        )
        self.assertEqual(btn.disabled, "")
        self.assertIsNotNone(btn.url)
        self.assertTrue(btn.perms.add)
        self.assertFalse(btn.perms.change)
        self.assertFalse(btn.perms.view)
        self.assertFalse(btn.perms.view_only)

        qs = urlparse(btn.url).query
        keys = list(parse_qs(qs, keep_blank_values=True).keys())
        keys.sort()
        self.assertEqual(
            keys,
            [
                "appointment",
                "next",
                "registered_subject",
                "sender",
                "subject_identifier",
                "title",
                "visit_code_sequence",
                "visit_schedule",
            ],
        )
        for v in parse_qs(qs, keep_blank_values=True).values():
            self.assertTrue(v[0])
