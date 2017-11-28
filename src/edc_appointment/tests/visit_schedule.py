from dateutil.relativedelta import relativedelta

from edc_visit_schedule import VisitSchedule, Schedule, Visit
from edc_visit_schedule import FormsCollection, Crf, Requisition
from pprint import pprint


crfs = FormsCollection(
    Crf(show_order=1, model='edc_metadata.crfone', required=True),
    Crf(show_order=2, model='edc_metadata.crftwo', required=True),
    Crf(show_order=3, model='edc_metadata.crfthree', required=True),
    Crf(show_order=4, model='edc_metadata.crffour', required=True),
    Crf(show_order=5, model='edc_metadata.crffive', required=True),
)

requisitions = FormsCollection(
    Requisition(
        show_order=10, model='edc_metadata.subjectrequisition',
        panel='one', required=True, additional=False),
    Requisition(
        show_order=20, model='edc_metadata.subjectrequisition',
        panel='two', required=True, additional=False),
    Requisition(
        show_order=30, model='edc_metadata.subjectrequisition',
        panel='three', required=True, additional=False),
    Requisition(
        show_order=40, model='edc_metadata.subjectrequisition',
        panel='four', required=True, additional=False),
    Requisition(
        show_order=50, model='edc_metadata.subjectrequisition',
        panel='five', required=True, additional=False),
    Requisition(
        show_order=60, model='edc_metadata.subjectrequisition',
        panel='six', required=True, additional=False),
)

visit_schedule1 = VisitSchedule(
    name='visit_schedule1',
    visit_model='edc_appointment.subjectvisit',
    offstudy_model='edc_appointment.subjectoffstudy')

visit_schedule2 = VisitSchedule(
    name='visit_schedule2',
    visit_model='edc_appointment.subjectvisit',
    offstudy_model='edc_appointment.subjectoffstudy')

schedule1 = Schedule(
    name='schedule1',
    enrollment_model='edc_appointment.enrollment1',
    disenrollment_model='edc_appointment.disenrollment1')

schedule2 = Schedule(
    name='schedule2',
    enrollment_model='edc_appointment.enrollment2',
    disenrollment_model='edc_appointment.disenrollment2')


visits = []
for index in range(0, 4):
    visits.append(
        Visit(
            code=f'{index + 1}000',
            title=f'Day {index + 1}',
            timepoint=index,
            rbase=relativedelta(days=index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            requisitions=requisitions,
            crfs=crfs,
            allow_unscheduled=True))
for visit in visits:
    schedule1.add_visit(visit)

visits = []
for index in range(4, 8):
    visits.append(
        Visit(
            code=f'{index + 1}000',
            title=f'Day {index + 1}',
            timepoint=index,
            rbase=relativedelta(days=index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            requisitions=requisitions,
            crfs=crfs))
for visit in visits:
    schedule2.add_visit(visit)

visit_schedule1.add_schedule(schedule1)
visit_schedule2.add_schedule(schedule2)
