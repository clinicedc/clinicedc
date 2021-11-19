from django.db.models.signals import pre_save
from django.test import TestCase, tag
from edc_appointment.creators import AppointmentsCreator
from edc_appointment.models import Appointment
from edc_constants.constants import NO, YES
from edc_facility import import_holidays
from edc_pharmacy.exceptions import (
    ActivePrescriptionRefillExists,
    NextPrescriptionRefillError,
)
from edc_pharmacy.models import (
    DosageGuideline,
    Formulation,
    FormulationType,
    FrequencyUnits,
    Medication,
    MedicationOrder,
    Route,
    Rx,
    RxRefill,
    Units,
)
from edc_pharmacy.tests.models import StudyMedication, SubjectVisit
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..visit_schedule import schedule, visit_schedule


class TestMedicationCrf(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        pre_save.disconnect(dispatch_uid="requires_consent_on_pre_save")

    def setUp(self) -> None:
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False

        site_visit_schedules.register(visit_schedule)
        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)
        report_datetime = get_utcnow()
        creator = AppointmentsCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule=visit_schedule,
            schedule=schedule,
            report_datetime=report_datetime,
        )
        creator.create_appointments(base_appt_datetime=report_datetime)

        self.assertGreater(
            Appointment.objects.filter(
                subject_identifier=self.subject_identifier
            ).count(),
            0,
        )

        self.medication = Medication.objects.create(
            name="Flucytosine",
        )

        self.formulation = Formulation.objects.create(
            medication=self.medication,
            strength=500,
            units=Units.objects.get(name="mg"),
            route=Route.objects.get(display_name="Oral"),
            formulation_type=FormulationType.objects.get(display_name__iexact="Tablet"),
        )

        self.dosage_guideline_100 = DosageGuideline.objects.create(
            medication=self.medication,
            dose_per_kg=100,
            dose_units=Units.objects.get(name="mg"),
            frequency=1,
            frequency_units=FrequencyUnits.objects.get(name="day"),
        )

        self.dosage_guideline_200 = DosageGuideline.objects.create(
            medication=self.medication,
            dose_per_kg=100,
            dose_units=Units.objects.get(name="mg"),
            frequency=2,
            frequency_units=FrequencyUnits.objects.get(name="day"),
        )

        self.rx = Rx.objects.create(
            subject_identifier=self.subject_identifier,
            weight_in_kgs=40,
            report_datetime=report_datetime,
            medication=self.medication,
        )

    @tag("35")
    def test_ok(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        obj = StudyMedication.objects.create(
            subject_visit=subject_visit,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
        )
        self.assertIsNotNone(obj.number_of_days)
        self.assertEqual(obj.number_of_days, 7)

    @tag("35")
    def test_for_all_appts(self):
        """Assert for all appointments.

        Captures exception at last appointment where "next" is none
        """
        for appointment in Appointment.objects.all().order_by("timepoint"):
            subject_visit = SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=appointment.appt_datetime,
                reason=SCHEDULED,
            )
            if not appointment.next:
                self.assertRaises(
                    NextPrescriptionRefillError,
                    StudyMedication.objects.create,
                    subject_visit=subject_visit,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                    order_next=YES,
                    next_dosage_guideline=self.dosage_guideline_100,
                    next_formulation=self.formulation,
                )
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                    next_dosage_guideline=None,
                    next_formulation=None,
                    order_next=NO,
                )
            else:
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                    order_next=YES,
                    next_dosage_guideline=self.dosage_guideline_100,
                    next_formulation=self.formulation,
                )

    @tag("35")
    def test_refill_creates_next_refill(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        self.assertEqual(RxRefill.objects.all().count(), 0)
        StudyMedication.objects.create(
            subject_visit=subject_visit,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
        )
        self.assertEqual(RxRefill.objects.all().count(), 2)

    @tag("35")
    def test_refill_creates_next_refill_for_next_dosage(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        StudyMedication.objects.create(
            subject_visit=subject_visit,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
        )
