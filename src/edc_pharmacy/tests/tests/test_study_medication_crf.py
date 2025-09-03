from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import override_settings, tag, TestCase

from edc_action_item.site_action_items import site_action_items
from edc_appointment.constants import INCOMPLETE_APPT
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.models import Appointment
from edc_appointment.utils import get_next_appointment
from edc_consent import site_consents
from edc_constants.constants import YES
from edc_facility.import_holidays import import_holidays
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
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED
from tests.consents import consent_v1
from tests.forms import StudyMedicationForm
from tests.helper import Helper
from tests.models import StudyMedication, SubjectVisit
from tests.visit_schedules.visit_schedule import get_visit_schedule

utc_tz = ZoneInfo("UTC")


@tag("pharmacy")
@override_settings(SITE_ID=10)
@time_machine.travel(datetime(2025, 6, 11, 8, 00, tzinfo=utc_tz))
class TestMedicationCrf(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_action_items.autodiscover()
        # pre_save.disconnect(dispatch_uid="requires_consent_on_pre_save")

    def setUp(self) -> None:
        site_consents.registry = {}
        site_consents.register(consent_v1)

        visit_schedule = get_visit_schedule(consent_v1, visit_count=5)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)

        helper = Helper()
        subject_consent = helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )
        self.subject_identifier = subject_consent.subject_identifier
        self.consent_datetime = subject_consent.consent_datetime

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
            report_datetime=self.consent_datetime,
            rx_date=self.consent_datetime.date(),
        )
        self.rx.medications.add(self.medication)

    def test_ok(self):
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]
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
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )

        obj = StudyMedication(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime,
            refill_start_datetime=datetime(
                self.rx.rx_date.year,
                self.rx.rx_date.month,
                self.rx.rx_date.day,
                0,
                0,
                0,
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
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]
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
            refill_start_datetime=subject_visit.report_datetime
            + relativedelta(years=1),
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
        for appointment in Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        ):
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
        self.assertEqual(
            RxRefill.objects.all().count(), Appointment.objects.all().count() - 1
        )

    def test_rx_refill_start_datetimes_are_greater(self):
        for appointment in Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        ):
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
        for appointment in Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        ):
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

    @tag("2001")
    def test_insert_unscheduled_appt_refill(self):
        for appointment in Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        ):
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

        for appointment in Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        ):
            appointment.appt_status = INCOMPLETE_APPT
            appointment.save_base(update_fields=["appt_status"])

        prev_obj = None
        for obj in StudyMedication.objects.all().order_by("refill_start_datetime"):
            if not prev_obj:
                prev_obj = obj
                continue
        appointment_before = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[1]
        appointment_after = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[2]
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

        self.assertEqual(Appointment.objects.all().count(), 6)
        self.assertEqual(RxRefill.objects.all().count(), 5)

        prev_obj = None
        for obj in StudyMedication.objects.all().order_by("refill_start_datetime"):
            if not prev_obj:
                prev_obj = obj
                continue
            self.assertLess(prev_obj.refill_start_datetime, obj.refill_start_datetime)
            self.assertLessEqual(
                prev_obj.refill_end_datetime, obj.refill_start_datetime
            )
            self.assertLess(prev_obj.refill_end_datetime, obj.refill_end_datetime)
            prev_obj = obj

        prev_obj = None
        for obj in RxRefill.objects.all().order_by("refill_start_datetime"):
            if not prev_obj:
                prev_obj = obj
                continue
            self.assertLess(prev_obj.refill_start_datetime, obj.refill_start_datetime)
            self.assertLessEqual(
                prev_obj.refill_end_datetime, obj.refill_start_datetime
            )
            self.assertLess(prev_obj.refill_end_datetime, obj.refill_end_datetime)
            prev_obj = obj

    def test_for_all_appts(self):
        """Assert for all appointments.

        Captures exception at last appointment where "next" is none
        """
        for appointment in Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        ):
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
        self.study_open_datetime = ResearchProtocolConfig().study_open_datetime
        self.study_close_datetime = ResearchProtocolConfig().study_close_datetime
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]
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
            site=Site.objects.get(id=settings.SITE_ID),
        )

        form = StudyMedicationForm(data=data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_inserts_refill(self):
        # 1000
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[0]
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
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[1]
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
        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[2]
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
            site=Site.objects.get(id=settings.SITE_ID),
        )
        # self.assertRaises(
        #     NextStudyMedicationError, StudyMedication.objects.create, **opts
        # )
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()

        self.assertEqual(RxRefill.objects.all().count(), 2)
        refills = RxRefill.objects.all().order_by("refill_start_datetime")
        self.assertEqual(refills[0].dosage_guideline, self.dosage_guideline_100)
        self.assertEqual(refills[1].dosage_guideline, self.dosage_guideline_200)

        # insert unscheduled appt between 2000 and 3000

        appointment = Appointment.objects.all().order_by(
            "timepoint", "visit_code_sequence"
        )[1]
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
