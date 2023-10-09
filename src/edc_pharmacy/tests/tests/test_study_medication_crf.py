from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
from django.db.models.signals import pre_save
from django.test import TestCase, override_settings
from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.models import Appointment
from edc_appointment.tests.helper import Helper
from edc_appointment.utils import get_next_appointment
from edc_consent.tests.consent_test_utils import consent_object_factory
from edc_constants.constants import YES
from edc_facility import import_holidays
from edc_protocol import Protocol
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED

from edc_pharmacy.exceptions import NextStudyMedicationError, StudyMedicationError
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
from ..visit_schedule import visit_schedule


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
        self.registration_datetime = get_utcnow() - relativedelta(years=5)
        RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier,
            registration_datetime=self.registration_datetime,
            consent_datetime=self.registration_datetime,
        )
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            now=get_utcnow() - relativedelta(years=5),
        )
        self.helper.consent_and_put_on_schedule(
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
        )
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
            refill_start_datetime=subject_visit.report_datetime,
            refill_end_datetime=get_next_appointment(
                appointment, include_interim=True
            ).appt_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
        )
        obj.save()

        # calc num of days until next visit
        number_of_days = (
            get_next_appointment(
                obj.subject_visit.appointment, include_interim=True
            ).appt_datetime
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
            refill_start_datetime=datetime(
                self.rx.rx_date.year, self.rx.rx_date.month, self.rx.rx_date.day, 0, 0, 0
            ).astimezone(ZoneInfo("UTC"))
            - relativedelta(years=1),
            refill_end_datetime=get_next_appointment(
                appointment, include_interim=True
            ).appt_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
        )
        with self.assertRaises(StudyMedicationError):
            obj.save()

    def test_refill_for_expired_rx(self):
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        self.rx.rx_expiration_date = subject_visit.report_datetime.date()
        self.rx.save()
        self.rx.refresh_from_db()

        obj = StudyMedication(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_start_datetime=subject_visit.report_datetime + relativedelta(years=1),
            refill_end_datetime=get_next_appointment(
                subject_visit.appointment, include_interim=True
            ).appt_datetime
            + relativedelta(years=1),
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
        )
        with self.assertRaises(StudyMedicationError):
            obj.save()

    def test_for_each_appt_creates_rxrefill_thru_studymedication(self):
        """Create one refill per appointment.

        Last appt does not get a refill
        """
        for appointment in Appointment.objects.all().order_by("timepoint"):
            subject_visit = SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=appointment.appt_datetime,
                reason=SCHEDULED,
            )
            if appointment.next:
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_start_datetime=subject_visit.report_datetime,
                    refill_end_datetime=get_next_appointment(
                        appointment, include_interim=True
                    ).appt_datetime,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                )
        self.assertEqual(
            StudyMedication.objects.all().count(), Appointment.objects.all().count() - 1
        )
        self.assertEqual(RxRefill.objects.all().count(), Appointment.objects.all().count() - 1)

    def test_rx_refill_start_datetimes_are_greater(self):
        for appointment in Appointment.objects.all().order_by("timepoint"):
            subject_visit = SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=appointment.appt_datetime,
                reason=SCHEDULED,
            )
            if appointment.next:
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_start_datetime=subject_visit.report_datetime,
                    refill_end_datetime=get_next_appointment(
                        appointment, include_interim=True
                    ).appt_datetime,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                )

        # check dates
        for obj in RxRefill.objects.all().order_by("refill_start_datetime"):
            self.assertLess(obj.refill_start_datetime, obj.refill_end_datetime)

        refill_start_datetimes = [
            obj.refill_start_datetime
            for obj in RxRefill.objects.all().order_by("refill_start_datetime")
        ]
        last_dt = None
        for dt in refill_start_datetimes:
            if not last_dt:
                last_dt = dt
                continue
            self.assertGreater(dt, last_dt)
            last_dt = dt

    def test_next_previous_refill(self):
        for appointment in Appointment.objects.all().order_by("timepoint"):
            subject_visit = SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=appointment.appt_datetime,
                reason=SCHEDULED,
            )
            if appointment.next:
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_start_datetime=subject_visit.report_datetime,
                    refill_end_datetime=get_next_appointment(
                        appointment, include_interim=True
                    ).appt_datetime
                    - relativedelta(minutes=1),
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                )
        obj0 = StudyMedication.objects.all().order_by("refill_start_datetime")[0]
        obj1 = StudyMedication.objects.all().order_by("refill_start_datetime")[1]
        self.assertEqual(obj0.next.id, obj1.id)
        self.assertEqual(obj0.id, obj1.previous.id)

    def test_insert_unscheduled_appt_refill(self):
        for appointment in Appointment.objects.all().order_by("timepoint"):
            subject_visit = SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=appointment.appt_datetime,
                reason=SCHEDULED,
            )
            if appointment.next:
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_start_datetime=subject_visit.report_datetime,
                    refill_end_datetime=get_next_appointment(
                        appointment, include_interim=True
                    ).appt_datetime
                    - relativedelta(minutes=1),
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                )

        for appointment in Appointment.objects.all():
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save_base(update_fields=["appt_status"])

        prev_obj = None
        for obj in StudyMedication.objects.all().order_by("refill_start_datetime"):
            if not prev_obj:
                prev_obj = obj
                continue
        appointment_before = Appointment.objects.all().order_by("timepoint")[1]
        appointment_after = Appointment.objects.all().order_by("timepoint")[2]
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment_before.subject_identifier,
            visit_schedule_name=appointment_before.visit_schedule_name,
            schedule_name=appointment_before.schedule_name,
            visit_code=appointment_before.visit_code,
            suggested_visit_code_sequence=appointment_before.visit_code_sequence + 1,
            facility=appointment_before.facility,
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=creator.appointment,
            report_datetime=creator.appointment.appt_datetime,
            reason=UNSCHEDULED,
        )
        study_medication = StudyMedication(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_start_datetime=subject_visit.report_datetime,
            refill_end_datetime=appointment_after.appt_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
        )
        study_medication.save()

        self.assertEqual(Appointment.objects.all().count(), 4)
        self.assertEqual(RxRefill.objects.all().count(), 3)

        prev_obj = None
        for obj in StudyMedication.objects.all().order_by("refill_start_datetime"):
            if not prev_obj:
                prev_obj = obj
                continue
            self.assertLess(prev_obj.refill_start_datetime, obj.refill_start_datetime)
            self.assertLess(prev_obj.refill_end_datetime, obj.refill_start_datetime)
            self.assertLess(prev_obj.refill_end_datetime, obj.refill_end_datetime)
            prev_obj = obj

        prev_obj = None
        for obj in RxRefill.objects.all().order_by("refill_start_datetime"):
            if not prev_obj:
                prev_obj = obj
                continue
            self.assertLess(prev_obj.refill_start_datetime, obj.refill_start_datetime)
            self.assertLess(prev_obj.refill_end_datetime, obj.refill_start_datetime)
            self.assertLess(prev_obj.refill_end_datetime, obj.refill_end_datetime)
            prev_obj = obj

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
                    NextStudyMedicationError,
                    StudyMedication.objects.create,
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_start_datetime=subject_visit.report_datetime,
                    refill_end_datetime=None,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                )
            else:
                StudyMedication.objects.create(
                    subject_visit=subject_visit,
                    report_datetime=subject_visit.report_datetime,
                    refill_start_datetime=subject_visit.report_datetime,
                    refill_end_datetime=get_next_appointment(
                        subject_visit.appointment, include_interim=True
                    ).appt_datetime,
                    dosage_guideline=self.dosage_guideline_100,
                    formulation=self.formulation,
                )

    def test_study_medication_form_baseline(self):
        self.study_open_datetime = Protocol().study_open_datetime
        self.study_close_datetime = Protocol().study_close_datetime
        consent_object_factory(
            model="edc_pharmacy.subjectconsent",
            start=self.study_open_datetime,
            end=self.study_close_datetime,
        )

        appointment = Appointment.objects.all().order_by("timepoint")[0]
        next_appointment = get_next_appointment(appointment, include_interim=True)
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        data = dict(
            subject_visit=subject_visit,
            refill=YES,
            report_datetime=subject_visit.report_datetime,
            refill_start_datetime=subject_visit.report_datetime,
            refill_end_datetime=next_appointment.appt_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
            refill_to_next_visit=YES,
            roundup_divisible_by=32,
        )

        form = StudyMedicationForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_inserts_refill(self):
        # 1000
        appointment = Appointment.objects.all().order_by("timepoint")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        self.assertEqual(RxRefill.objects.all().count(), 0)
        StudyMedication.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_start_datetime=subject_visit.report_datetime,
            refill_end_datetime=get_next_appointment(
                appointment, include_interim=True
            ).appt_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
        )
        self.assertEqual(RxRefill.objects.all().count(), 1)
        refills = RxRefill.objects.all().order_by("refill_start_datetime")
        self.assertEqual(refills[0].dosage_guideline, self.dosage_guideline_100)

        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        # 2000
        appointment = Appointment.objects.all().order_by("timepoint")[1]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )

        StudyMedication.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_start_datetime=subject_visit.report_datetime,
            refill_end_datetime=get_next_appointment(
                appointment, include_interim=True
            ).appt_datetime,
            dosage_guideline=self.dosage_guideline_200,
            formulation=self.formulation,
        )

        self.assertEqual(RxRefill.objects.all().count(), 2)

        refills = RxRefill.objects.all().order_by("refill_start_datetime")
        self.assertEqual(refills[0].dosage_guideline, self.dosage_guideline_100)
        self.assertEqual(refills[1].dosage_guideline, self.dosage_guideline_200)
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        # 3000
        appointment = Appointment.objects.all().order_by("timepoint")[2]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )

        opts = dict(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_start_datetime=subject_visit.report_datetime,
            refill_end_datetime=None,
            dosage_guideline=self.dosage_guideline_200,
            formulation=self.formulation,
        )
        self.assertRaises(NextStudyMedicationError, StudyMedication.objects.create, **opts)
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        self.assertEqual(RxRefill.objects.all().count(), 2)
        refills = RxRefill.objects.all().order_by("refill_start_datetime")
        self.assertEqual(refills[0].dosage_guideline, self.dosage_guideline_100)
        self.assertEqual(refills[1].dosage_guideline, self.dosage_guideline_200)

        # insert unscheduled appt between 2000 and 3000

        appointment = Appointment.objects.all().order_by("timepoint")[1]
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
            facility=appointment.facility,
        )

        subject_visit = SubjectVisit.objects.create(
            appointment=creator.appointment,
            report_datetime=creator.appointment.appt_datetime,
            reason=UNSCHEDULED,
        )

        StudyMedication.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_start_datetime=subject_visit.report_datetime,
            refill_end_datetime=get_next_appointment(
                creator.appointment, include_interim=True
            ).appt_datetime,
            dosage_guideline=self.dosage_guideline_100,
            formulation=self.formulation,
        )

        self.assertEqual(StudyMedication.objects.all().count(), 3)

        self.assertEqual(
            self.dosage_guideline_100,
            StudyMedication.objects.all()
            .order_by("refill_start_datetime")[0]
            .dosage_guideline,
        )
        self.assertEqual(
            self.dosage_guideline_200,
            StudyMedication.objects.all()
            .order_by("refill_start_datetime")[1]
            .dosage_guideline,
        )
        self.assertEqual(
            self.dosage_guideline_100,
            StudyMedication.objects.all()
            .order_by("refill_start_datetime")[2]
            .dosage_guideline,
        )
