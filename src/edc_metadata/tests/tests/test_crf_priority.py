from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings, tag

from edc_metadata.admin.crf_priority import CrfPriorityForm
from edc_metadata.constants import CRF
from edc_metadata.models import CrfPriority


@tag("metadata")
@override_settings(SITE_ID=10)
class TestCrfPriority(TestCase):
    def test_create_and_defaults(self):
        obj = CrfPriority.objects.create(
            model="clinicedc_tests.crfone",
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        self.assertEqual(obj.tier, 2)
        self.assertTrue(obj.active)
        self.assertEqual(obj.metadata_kind, CRF)
        self.assertIn("clinicedc_tests.crfone", str(obj))

    def test_unique_per_model_schedule_kind(self):
        opts = dict(
            model="clinicedc_tests.crfone",
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        CrfPriority.objects.create(**opts)
        with transaction.atomic(), self.assertRaises(IntegrityError):
            CrfPriority.objects.create(**opts)

    def test_admin_form_uses_explicit_fields_without_audit_fields(self):
        # audit fields are system columns and must never be exposed on a
        # user-facing ModelForm.
        fields = set(CrfPriorityForm.base_fields)
        self.assertEqual(
            fields,
            {
                "model",
                "visit_schedule_name",
                "schedule_name",
                "metadata_kind",
                "tier",
                "active",
            },
        )
        for audit_field in (
            "created",
            "modified",
            "user_created",
            "user_modified",
            "hostname_created",
            "device_created",
        ):
            self.assertNotIn(audit_field, fields)
