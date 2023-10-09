from django.test import TestCase
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_constants.constants import NEVER, NO, OTHER, YES
from edc_facility import import_holidays
from edc_list_data import site_list_data
from edc_reference import site_reference_configs
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from edc_adherence import list_data
from edc_adherence.models import NonAdherenceReasons
from edc_adherence.tests.admin import MedicationAdherenceAdmin, my_admin_site

from ..forms import MedicationAdherenceForm
from ..models import MedicationAdherence, SubjectVisit
from ..visit_schedules import visit_schedule


class TestAdherence(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self) -> None:
        site_list_data.initialize()
        site_list_data.register(list_data, app_name="edc_adherence")
        site_list_data.load_data()
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_adherence.subjectvisit"}
        )
        self.subject_identifier = "1234"
        self.helper = Helper(subject_identifier=self.subject_identifier)
        self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            age_in_years=25,
        )
        appointments = Appointment.objects.filter(subject_identifier=self.subject_identifier)
        self.subject_visit = SubjectVisit.objects.create(appointment=appointments[0])

    def test_ok(self):
        opts = dict(
            visual_score_slider=90,
            visual_score_confirmed=90,
            last_missed_pill=NEVER,
            pill_count_performed=YES,
            pill_count=30,
            other_missed_pill_reason=None,
        )
        obj = MedicationAdherence(subject_visit=self.subject_visit, **opts)
        obj.save()
        obj.delete()
        opts = dict(
            visual_score_slider=90,
            visual_score_confirmed=90,
            last_missed_pill="today",
            pill_count_performed=YES,
            pill_count=20,
            other_missed_pill_reason=None,
        )
        obj = MedicationAdherence(subject_visit=self.subject_visit, **opts)
        obj.save()
        obj.missed_pill_reason.add(NonAdherenceReasons.objects.get(name="make_me_ill"))

    def test_form(self):
        data = dict(
            visual_score_slider=90,
            visual_score_confirmed=90,
            last_missed_pill=NEVER,
            pill_count_performed=YES,
            pill_count=30,
            other_missed_pill_reason=None,
            subject_visit=self.subject_visit,
            report_datetime=self.subject_visit.report_datetime,
        )
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertDictEqual(form._errors, {})

        data.update(visual_score_confirmed=80)
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertIn("visual_score_confirmed", form._errors)
        data.update(visual_score_confirmed=90)

        data.update(last_missed_pill="today")
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertIn("missed_pill_reason", form._errors)

        data.update(missed_pill_reason=NonAdherenceReasons.objects.filter(name=OTHER))
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertIn("other_missed_pill_reason", form._errors)

        data.update(
            other_missed_pill_reason="i feel the pull on the rope, let me off at the rainbow"
        )
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertDictEqual(form._errors, {})

    def test_admin(self):
        my_admin_site.register(MedicationAdherence, MedicationAdherenceAdmin)
        MedicationAdherenceAdmin(MedicationAdherence, my_admin_site)

    def test_pill_count(self):
        data = dict(
            visual_score_slider=90,
            visual_score_confirmed=90,
            last_missed_pill=NEVER,
            other_missed_pill_reason=None,
            subject_visit=self.subject_visit,
            report_datetime=self.subject_visit.report_datetime,
        )
        data.update(
            pill_count_performed=YES,
            pill_count=0,
        )
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

        data.update(pill_count=1)
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

        data.update(pill_count_performed=NO, pill_count=0)
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertIn("pill_count", form._errors)

        data.update(pill_count_performed=NO, pill_count=None)
        form = MedicationAdherenceForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
