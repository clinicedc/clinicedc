import uuid

from edc_appointment.models import Appointment
from edc_base.utils import get_utcnow
from edc_registration.models import RegisteredSubject

from .models import ListModel, SubjectVisit, Crf
from .models import CrfTwo, CrfOne, CrfThree, CrfInline


class Helper:

    def create_crf(self, i=None):
        i = i or 0
        subject_identifier = f'12345{i}'
        visit_code = f'{i}000'
        RegisteredSubject.objects.create(
            subject_identifier=subject_identifier)
        appointment = Appointment.objects.create(
            subject_identifier=subject_identifier,
            visit_code=visit_code,
            appt_datetime=get_utcnow())
        self.thing_one = ListModel.objects.create(
            name=f'thing_one_{i}', short_name=f'thing_one_{i}')
        self.thing_two = ListModel.objects.create(
            name=f'thing_two_{i}', short_name=f'thing_two_{i}')
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            subject_identifier=subject_identifier,
            report_datetime=get_utcnow())
        Crf.objects.create(
            subject_visit=self.subject_visit,
            char1=f'char{i}',
            date1=get_utcnow(),
            int1=i,
            uuid1=uuid.uuid4())
        crf_one = CrfOne.objects.create(
            subject_visit=self.subject_visit,
            dte=get_utcnow())
        crf_two = CrfTwo.objects.create(
            subject_visit=self.subject_visit,
            dte=get_utcnow())
        CrfThree.objects.create(
            subject_visit=self.subject_visit,
            UPPERCASE=get_utcnow())
        CrfInline.objects.create(
            crf_one=crf_one,
            crf_two=crf_two,
            dte=get_utcnow())
