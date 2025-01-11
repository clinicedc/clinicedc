from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase, override_settings
from edc_appointment.models import Appointment
from edc_consent import site_consents
from edc_consent.consent_definition import ConsentDefinition
from edc_constants.constants import FEMALE, MALE
from edc_visit_tracking.constants import SCHEDULED

from edc_action_item.models import ActionItem
from edc_action_item.utils import (
    get_parent_reference_obj,
    get_reference_obj,
    get_related_reference_obj,
)

from ..action_items import CrfOneAction, register_actions
from ..models import CrfOne, CrfTwo, FormOne, FormTwo
from ..test_case_mixin import TestCaseMixin

test_datetime = datetime(2019, 6, 11, 8, 00, tzinfo=ZoneInfo("UTC"))


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=test_datetime - relativedelta(years=3),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=test_datetime + relativedelta(years=3),
)
class TestHelpers(TestCaseMixin, TestCase):
    def setUp(self):
        site_consents.registry = {}
        register_actions()
        self.subject_identifier = self.fake_enroll()
        self.form_one = FormOne.objects.create(subject_identifier=self.subject_identifier)
        self.action_item = ActionItem.objects.get(
            action_identifier=self.form_one.action_identifier
        )

    def test_new_action(self):
        CrfOneAction(subject_identifier=self.subject_identifier)
        self.assertIsNone(get_reference_obj(None))
        self.assertIsNone(get_parent_reference_obj(None))
        self.assertIsNone(get_related_reference_obj(None))

    def test_create_parent_reference_model_instance_then_delete(self):
        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)
        self.assertEqual(get_reference_obj(action_item), form_two)
        form_two.delete()
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)
        self.assertIsNone(get_reference_obj(action_item))

    def test_create_parent_reference_model_instance(self):
        form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(action_identifier=form_two.action_identifier)
        self.assertEqual(get_reference_obj(action_item), form_two)
        self.assertEqual(get_parent_reference_obj(action_item), self.form_one)
        self.assertEqual(get_related_reference_obj(action_item), self.form_one)

    def test_create_next_parent_reference_model_instance(self):
        first_form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        second_form_two = FormTwo.objects.create(
            form_one=self.form_one, subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(
            action_identifier=second_form_two.action_identifier
        )
        self.assertEqual(get_reference_obj(action_item), second_form_two)
        self.assertEqual(get_parent_reference_obj(action_item), first_form_two)
        self.assertEqual(get_related_reference_obj(action_item), self.form_one)

    def test_reference_as_crf(self):
        consent_v1 = ConsentDefinition(
            "edc_action_item.subjectconsentv1",
            version="1",
            start=test_datetime,
            end=test_datetime + relativedelta(years=3),
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        self.enroll(consent_datetime=test_datetime, cdef=consent_v1)
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        traveller = time_machine.travel(appointment.appt_datetime)
        traveller.start()
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        action_item = ActionItem.objects.get(action_identifier=crf_one.action_identifier)
        self.assertEqual(get_reference_obj(action_item), crf_one)
        self.assertIsNone(get_parent_reference_obj(action_item))
        self.assertIsNone(get_related_reference_obj(action_item))
        traveller.stop()

    def test_reference_as_crf_create_next_model_instance(self):
        consent_v1 = ConsentDefinition(
            "edc_action_item.subjectconsentv1",
            version="1",
            start=test_datetime,
            end=test_datetime + relativedelta(years=3),
            age_min=18,
            age_is_adult=18,
            age_max=64,
            gender=[MALE, FEMALE],
        )
        self.enroll(consent_datetime=test_datetime, cdef=consent_v1)
        traveller = time_machine.travel(test_datetime)
        traveller.start()
        appointment = Appointment.objects.all().order_by("timepoint", "visit_code_sequence")[0]
        subject_visit = django_apps.get_model(
            "edc_visit_tracking.subjectvisit"
        ).objects.create(appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        crf_two = CrfTwo.objects.create(subject_visit=subject_visit)
        action_item = ActionItem.objects.get(action_identifier=crf_two.action_identifier)
        self.assertEqual(get_reference_obj(action_item), crf_two)
        self.assertEqual(get_parent_reference_obj(action_item), crf_one)
        self.assertIsNone(get_related_reference_obj(action_item))
        traveller.stop()
