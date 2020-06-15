import uuid

from decimal import Decimal
from edc_appointment.creators import UnscheduledAppointmentCreator
from edc_utils import get_utcnow
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .models import ListModel, SubjectVisit, Crf
from .models import CrfTwo, CrfOne, CrfThree, CrfWithInline, ListOne, ListTwo
from .models import SubjectConsent, Appointment
from .visit_schedule import visit_schedule1


class Helper:
    def __init__(self, now=None, subject_identifier=None):
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule1)
        self.now = now or get_utcnow()
        self.subject_identifier = subject_identifier or uuid.uuid4().hex
        self.consent_and_put_on_schedule()
        self.subject_visit = None
        self.thing_one = None
        self.thing_two = None

    def consent_and_put_on_schedule(self, subject_identifier=None):
        subject_identifier = subject_identifier or self.subject_identifier
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier, consent_datetime=self.now
        )
        visit_schedule = site_visit_schedules.get_visit_schedule("visit_schedule1")
        schedule = visit_schedule.schedules.get("schedule1")
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        return subject_consent

    @staticmethod
    def add_unscheduled_appointment(appointment=None):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            facility=appointment.facility,
            timepoint=appointment.timepoint + Decimal("0.1"),
        )
        return creator.appointment

    def create_crfs(self, i):
        for appointment in Appointment.objects.all().order_by("visit_code"):
            SubjectVisit.objects.create(
                appointment=appointment,
                subject_identifier=appointment.subject_identifier,
                report_datetime=get_utcnow(),
            )
        for j in range(0, i - 1):
            appointment = Appointment.objects.all().order_by("visit_code")[j]
            self.subject_visit = SubjectVisit.objects.get(appointment=appointment)
            self.thing_one = ListModel.objects.create(
                display_name=f"thing_one_{appointment.visit_code}",
                name=f"thing_one_{appointment.visit_code}",
            )
            self.thing_two = ListModel.objects.create(
                display_name=f"thing_two_{appointment.visit_code}",
                name=f"thing_two_{appointment.visit_code}",
            )
            Crf.objects.create(
                subject_visit=self.subject_visit,
                char1=f"char{appointment.visit_code}",
                date1=get_utcnow(),
                int1=j,
                uuid1=uuid.uuid4(),
            )
            CrfOne.objects.create(subject_visit=self.subject_visit, dte=get_utcnow())
            CrfTwo.objects.create(subject_visit=self.subject_visit, dte=get_utcnow())
            CrfThree.objects.create(
                subject_visit=self.subject_visit, UPPERCASE=get_utcnow()
            )

        for i, appointment in enumerate(
            Appointment.objects.all().order_by("visit_code")
        ):
            if appointment != self.subject_visit.appointment:
                self.create_crf_with_inlines(appointment)

    @staticmethod
    def create_crf_with_inlines(appointment):
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=appointment.subject_identifier,
            report_datetime=get_utcnow(),
        )
        list_one = ListOne.objects.create(
            display_name=f"list_one{appointment.visit_code}",
            name=f"list_one{appointment.visit_code}",
        )
        list_two = ListTwo.objects.create(
            display_name=f"list_two{appointment.visit_code}",
            name=f"list_two{appointment.visit_code}",
        )
        CrfWithInline.objects.create(
            subject_visit=subject_visit,
            list_one=list_one,
            list_two=list_two,
            dte=get_utcnow(),
        )
