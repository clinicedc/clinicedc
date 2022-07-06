import uuid

from dateutil.relativedelta import relativedelta
from edc_appointment.models import Appointment
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow

from .models import (
    Crf,
    CrfInline,
    CrfOne,
    CrfThree,
    CrfTwo,
    ListModel,
    OnSchedule,
    SubjectVisit,
)


class Helper:
    @staticmethod
    def create_crf(i=None):
        i = i or 0
        subject_identifier = f"12345{i}"
        RegisteredSubject.objects.create(subject_identifier=subject_identifier)

        OnSchedule.objects.create(
            subject_identifier=subject_identifier,
            onschedule_datetime=get_utcnow() - relativedelta(years=1),
        )

        appointment = Appointment.objects.filter(
            subject_identifier=subject_identifier
        ).order_by("appt_datetime")[0]

        thing_one = ListModel.objects.create(
            display_name=f"thing_one_{i}", name=f"thing_one_{i}"
        )
        thing_two = ListModel.objects.create(
            display_name=f"thing_two_{i}", name=f"thing_two_{i}"
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=subject_identifier,
            report_datetime=get_utcnow(),
        )
        Crf.objects.create(
            subject_visit=subject_visit,
            char1=f"char{i}",
            date1=get_utcnow(),
            int1=i,
            uuid1=uuid.uuid4(),
        )
        crf_one = CrfOne.objects.create(subject_visit=subject_visit, dte=get_utcnow())
        crf_two = CrfTwo.objects.create(subject_visit=subject_visit, dte=get_utcnow())
        CrfThree.objects.create(subject_visit=subject_visit, UPPERCASE=get_utcnow())
        CrfInline.objects.create(crf_one=crf_one, crf_two=crf_two, dte=get_utcnow())
        return subject_visit, thing_one, thing_two
