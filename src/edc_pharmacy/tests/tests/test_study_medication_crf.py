from dateutil.relativedelta import relativedelta
from django.db.models.signals import pre_save
from django.test import TestCase, override_settings
from edc_appointment.creators import AppointmentsCreator
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_constants.constants import NO, YES
from edc_facility import import_holidays
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from edc_pharmacy.exceptions import (
    NextRefillError,
    PrescriptionExpired,
    PrescriptionNotStarted,
)
from edc_pharmacy.models import (
    DosageGuideline,
    Formulation,
    FormulationType,
    FrequencyUnits,
    Medication,
    Route,
    Rx,
    RxRefill,
    Units,
)

from ..forms import StudyMedicationForm
from ..models import StudyMedication, SubjectVisit
from ..visit_schedule import schedule, visit_schedule


@override_settings(SUBJECT_CONSENT_MODEL="edc_pharmacy.subjectconsent")
class TestMedicationCrf(TestCase):

    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        pre_save.disconnect(dispatch_uid="requires_consent_on_pre_save")

    def setUp(self) -> None:
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False

        site_visit_schedules.register(visit_schedule)
        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier,
            registration_datetime=get_utcnow() - relativedelta(years=5),
        )
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=get_utcnow() - relativedelta(years=6),
        )
        self.helper.consent_and_put_on_schedule(
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
        self.registration_datetime = get_utcnow() - relativedelta(years=5)
        creator = AppointmentsCreator(
            subject_identifier=self.subject_identifier,
            visit_schedule=visit_schedule,
            schedule=schedule,
            report_datetime=self.registration_datetime,
        )
        creator.create_appointments(base_appt_datetime=self.registration_datetime)

        self.assertGreater(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(),
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
            report_datetime=self.registration_datetime,
            rx_date=self.registration_datetime.date(),
        )
        self.rx.medications.add(self.medication)

    def test_ok(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )

        obj = StudyMedication(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_date=subject_visit.report_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
        )
        obj.save()

        # calc num of days until next visit
        number_of_days = (
            obj.subject_visit.appointment.next.appt_datetime
            - obj.subject_visit.appointment.appt_datetime
        ).days

        self.assertIsNotNone(obj.number_of_days)
        self.assertEqual(obj.number_of_days, number_of_days)
        self.assertGreater(obj.number_of_days, 0)

    def test_refill_before_rx(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )

        obj = StudyMedication(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_date=self.rx.rx_date - relativedelta(years=1),
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
        )
        with self.assertRaises(PrescriptionNotStarted):
            obj.save()

    def test_refill_for_expired_rx(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        self.rx.rx_expiration_date = subject_visit.report_datetime
        self.rx.save()
        self.rx.refresh_from_db()

        obj = StudyMedication(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_date=subject_visit.report_datetime + relativedelta(years=1),
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
        )
        with self.assertRaises(PrescriptionExpired):
            obj.save()

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
                    NextRefillError,
                    StudyMedication.objects.create,
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_date=subject_visit.report_datetime,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                    order_next=YES,
                    next_dosage_guideline=self.dosage_guideline_100,
                    next_formulation=self.formulation,
                )
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_date=subject_visit.report_datetime,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                    next_dosage_guideline=None,
                    next_formulation=None,
                    order_next=NO,
                )
            else:
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_date=subject_visit.report_datetime,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                    order_next=YES,
                    next_dosage_guideline=self.dosage_guideline_100,
                    next_formulation=self.formulation,
                )

    def test_refill_creates_next_refill(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        self.assertEqual(RxRefill.objects.all().count(), 0)
        StudyMedication.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_date=subject_visit.report_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
        )
        self.assertEqual(RxRefill.objects.all().count(), 2)

    def test_refill_creates_next_refill_for_next_dosage(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        StudyMedication.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_date=subject_visit.report_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
        )

    def test_study_medication_form_baseline(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_date=subject_visit.report_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            refill_to_next_visit=YES,
            order_next=YES,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
            roundup_divisible_by=32,
        )

        form = StudyMedicationForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_study_medication_form_not_order_next(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
        )
        data = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_date=subject_visit.report_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            refill_to_next_visit=YES,
            order_next=NO,
            next_dosage_guideline=self.dosage_guideline_200,
            next_formulation=self.formulation,
            roundup_divisible_by=32,
        )

        form = StudyMedicationForm(data=data)
        form.is_valid()
        self.assertIn("next_dosage_guideline", form._errors)

        data.update(next_dosage_guideline=None)
        form = StudyMedicationForm(data=data)
        form.is_valid()
        self.assertIn("next_formulation", form._errors)

        data.update(next_formulation=None)
        form = StudyMedicationForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)
