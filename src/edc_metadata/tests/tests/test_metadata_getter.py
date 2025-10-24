from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from clinicedc_tests.models import CrfFive, CrfFour, CrfThree
from django.test import TestCase, override_settings, tag

from edc_lab_panel.panels import fbc_panel, lft_panel, vl_panel
from edc_metadata.constants import REQUIRED
from edc_metadata.metadata import CrfMetadataGetter
from edc_metadata.next_form_getter import NextFormGetter

from .metadata_test_mixin import TestMetadataMixin

utc_tz = ZoneInfo("UTC")


@tag("metadata")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2019, 8, 11, 8, 00, tzinfo=utc_tz))
class TestMetadataGetter(TestMetadataMixin, TestCase):
    def test_objects_not_none_from_appointment(self):
        getter = CrfMetadataGetter(self.appointment)
        self.assertGreater(getter.metadata_objects.count(), 0)

    def test_next_object(self):
        getter = CrfMetadataGetter(self.appointment)
        visit = self.schedule.visits.get(getter.visit_code)
        objects = []
        for crf in visit.crfs:
            obj = getter.next_object(crf.show_order, entry_status=REQUIRED)
            if obj:
                objects.append(obj)
                self.assertIsNotNone(obj)
                self.assertGreater(obj.show_order, crf.show_order)
        self.assertEqual(len(objects), len(visit.crfs) - 1)

    def test_next_required_form(self):
        getter = NextFormGetter(appointment=self.appointment, model="clinicedc_tests.crffour")
        self.assertEqual(getter.next_form.model, "clinicedc_tests.crffive")

    def test_next_required_form2(self):
        crf_five = CrfFive.objects.create(subject_visit=self.subject_visit)
        getter = NextFormGetter(model_obj=crf_five)
        self.assertEqual(getter.next_form.model, "clinicedc_tests.crfsix")

    def test_next_required_form3(self):
        CrfFour.objects.create(subject_visit=self.subject_visit)
        CrfFive.objects.create(subject_visit=self.subject_visit)
        crf_three = CrfThree.objects.create(subject_visit=self.subject_visit)
        getter = NextFormGetter(model_obj=crf_three)
        self.assertEqual(getter.next_form.model, "clinicedc_tests.crfsix")

    def test_next_requisition(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="clinicedc_tests.subjectrequisition",
            panel_name=fbc_panel.name,
        )
        next_form = getter.next_form
        self.assertEqual(next_form.model, "clinicedc_tests.subjectrequisition")
        self.assertEqual(next_form.panel.name, lft_panel.name)

    def test_next_requisition_if_last(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="clinicedc_tests.subjectrequisition",
            panel_name=vl_panel.name,
        )
        next_form = getter.next_form
        self.assertIsNone(next_form)

    def test_next_requisition_if_not_in_visit(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="clinicedc_tests.subjectrequisition",
            panel_name="blah",
        )
        next_form = getter.next_form
        self.assertIsNone(next_form)
