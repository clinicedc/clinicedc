from __future__ import annotations

import uuid
from datetime import date, datetime
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.db import transaction
from faker import Faker

from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_appointment.models import Appointment
from edc_consent.consent_definition import ConsentDefinition
from edc_constants.constants import FEMALE, NO, SUBJECT, YES
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_tracking.models import SubjectVisit
from tests.consents import consent_v1
from tests.models import Alphabet, CrfFive, CrfFour, CrfSix, CrfThree, CrfWithInline2

fake = Faker()


class Helper:
    def __init__(self, now=None):
        self.now = now or get_utcnow()

    @property
    def screening_model_cls(self):
        """Returns a screening model class.

        Defaults to tests.subjectscreening
        """
        try:
            return django_apps.get_model(settings.SUBJECT_SCREENING_MODEL)
        except LookupError:
            return django_apps.get_model("tests.subjectscreening")

    def consent_and_put_on_schedule(
        self,
        visit_schedule_name: str = None,
        schedule_name: str = None,
        consent_definition: ConsentDefinition | None = None,
        age_in_years: int | None = None,
        report_datetime: datetime | None = None,
        gender: str = None,
        dob: date | None = None,
        guardian_name: str | None = None,
        is_literate: str | None = None,
        identity_type: str | None = None,
        alive: str | None = None,
        onschedule_datetime: datetime | None = None,
    ):

        if dob:
            age_in_years = get_utcnow().year - dob.year
        if not consent_definition:
            consent_definition = consent_v1
        subject_screening, first_name, last_name = self.screen_subject(
            report_datetime=report_datetime,
            age_in_years=age_in_years,
            gender=gender,
            alive=alive,
        )

        subject_consent = self.consent_subject(
            consent_definition=consent_definition,
            subject_screening=subject_screening,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            guardian_name=guardian_name,
            is_literate=is_literate,
            identity_type=identity_type,
        )
        self.put_subject_on_schedule(
            subject_consent=subject_consent,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            onschedule_datetime=onschedule_datetime,
        )
        return subject_consent

    def screen_subject(
        self,
        gender: str = None,
        age_in_years: int | None = None,
        report_datetime: datetime | None = None,
        alive: str | None = None,
    ):
        gender = gender or FEMALE
        age_in_years = age_in_years or 25
        report_datetime = report_datetime or self.now
        last_name = fake.last_name().replace(" ", "").upper()
        first_name = fake.first_name().replace(" ", "").upper()
        initials = f"{first_name[0]}{last_name[0]}".upper()
        alive = alive or YES

        while self.screening_model_cls.objects.filter(
            age_in_years=age_in_years, initials=initials
        ).exists():
            last_name = fake.last_name().replace(" ", "").upper()
            first_name = fake.first_name().replace(" ", "").upper()
            initials = f"{first_name[0]}{last_name[0]}".upper()

        subject_screening = self.screening_model_cls.objects.create(
            report_datetime=report_datetime or self.now,
            screening_identifier=uuid4(),
            age_in_years=age_in_years,
            initials=initials,
            gender=gender,
            alive=alive,
        )
        subject_screening.eligible = True
        subject_screening.eligible_datetime = subject_screening.report_datetime
        subject_screening.save_base(update_fields=["eligible", "eligible_datetime"])
        return subject_screening, first_name, last_name

    def consent_subject(
        self,
        consent_definition: ConsentDefinition | None = None,
        subject_screening=None,
        first_name: str = None,
        last_name: str = None,
        dob: date | None = None,
        guardian_name: str | None = None,
        is_literate: str | None = None,
        identity_type: str | None = None,
        consent_datetime: datetime | None = None,
    ):
        identity = str(uuid4())
        if not consent_definition:
            raise ValueError("Consent definition cannot be None")
        cdef = consent_definition
        with transaction.atomic():
            subject_consent = cdef.model_create(
                screening_identifier=subject_screening.screening_identifier,
                consent_datetime=consent_datetime or subject_screening.report_datetime,
                dob=(
                    dob
                    or self.now - relativedelta(years=subject_screening.age_in_years)
                ),
                identity=identity,
                confirm_identity=identity,
                identity_type="country_id" if identity_type is None else identity_type,
                gender=subject_screening.gender,
                first_name=first_name,
                last_name=last_name,
                initials=subject_screening.initials,
                guardian_name=guardian_name,
                is_literate=is_literate or YES,
                citizen=YES,
                is_dob_estimated="-",
                subject_type=SUBJECT,
                consent_reviewed=YES,
                study_questions=YES,
                assessment_score=YES,
                consent_signature=YES,
                consent_copy=YES,
                is_incarcerated=NO,
                language="en",
            )
        return subject_consent

    @staticmethod
    def put_subject_on_schedule(
        subject_consent=None,
        visit_schedule_name: str = None,
        schedule_name: str = None,
        onschedule_datetime: datetime | None = None,
    ):
        visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
        schedule = visit_schedule.schedules.get(schedule_name)
        schedule.put_on_schedule(
            subject_consent.subject_identifier,
            onschedule_datetime or subject_consent.consent_datetime,
            # consent_definition=subject_consent.consent_definition,
        )
        return None

    @staticmethod
    def add_unscheduled_appointment(
        appointment: Appointment | None = None,
        suggested_appt_datetime: datetime | None = None,
    ):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            suggested_appt_datetime=suggested_appt_datetime,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
            facility=appointment.facility,
        )
        return creator.appointment

    @staticmethod
    def create_crfs():
        for i, appointment in enumerate(Appointment.objects.all()):
            alphabet = Alphabet.objects.create(
                display_name=f"display_name{i}", name=f"name{i}"
            )
            subject_visit = SubjectVisit.objects.create(
                appointment=appointment, report_datetime=get_utcnow(), reason=SCHEDULED
            )
            CrfThree.objects.create(
                subject_visit=subject_visit,
                report_datetime=get_utcnow(),
                f1=f"char{i}",
                f4=i,
                f5=uuid.uuid4(),
            )
            crf_one = CrfFour.objects.create(
                subject_visit=subject_visit, report_datetime=get_utcnow()
            )
            CrfFive.objects.create(
                subject_visit=subject_visit, report_datetime=get_utcnow()
            )
            CrfSix.objects.create(
                subject_visit=subject_visit, report_datetime=get_utcnow()
            )
            CrfWithInline2.objects.create(
                crf_one=crf_one, alphabet=alphabet, dte=get_utcnow()
            )

    def enroll_to_baseline(self, **kwargs) -> SubjectVisit:
        """Enrolls with first appointment attended"""
        consent = self.consent_and_put_on_schedule(**kwargs)
        appointment = Appointment.objects.filter(
            subject_identifier=consent.subject_identifier
        ).order_by("appt_datetime")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=appointment.appt_datetime,
            reason=SCHEDULED,
        )
        return subject_visit
