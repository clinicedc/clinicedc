from edc_visit_schedule import FormsCollection, Crf, Requisition
from edc_visit_schedule import VisitSchedule, Schedule, Visit

from dateutil.relativedelta import relativedelta


crfs = FormsCollection(
    Crf(show_order=1, model='edc_metadata.crfone', required=True),
    Crf(show_order=2, model='edc_metadata.crftwo', required=True),
)

requisitions = FormsCollection(
    Requisition(
        show_order=10, model='edc_metadata.subjectrequisition',
        panel='one', required=True, additional=False),
)

visit_schedule1 = VisitSchedule(
    name='visit_schedule1',
    visit_model='edc_offstudy.subjectvisit',
    offstudy_model='edc_offstudy.subjectoffstudy')

schedule1 = Schedule(
    name='schedule1',
    enrollment_model='edc_offstudy.enrollment',
    disenrollment_model='edc_offstudy.disenrollment')

visit = Visit(
    code=f'1000',
    title=f'Day 1',
    timepoint=1,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=requisitions,
    crfs=crfs)
schedule1.add_visit(visit)
visit_schedule1.add_schedule(schedule1)
