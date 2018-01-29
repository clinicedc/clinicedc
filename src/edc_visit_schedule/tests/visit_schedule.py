from ..schedule import Schedule
from ..visit import FormsCollection, Crf, Visit
from ..visit_schedule import VisitSchedule

from dateutil.relativedelta import relativedelta


crfs = FormsCollection(
    Crf(show_order=1, model=f'edc_visit_tracking.crfone', required=True),
)


visit0 = Visit(
    code='1000',
    title='Day 1',
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name='default')

visit1 = Visit(
    code='2000',
    title='Day 2',
    timepoint=1,
    rbase=relativedelta(days=1),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name='default')

visit2 = Visit(
    code='3000',
    title='Day 3',
    timepoint=2,
    rbase=relativedelta(days=2),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name='default')

visit3 = Visit(
    code='4000',
    title='Day 4',
    timepoint=3,
    rbase=relativedelta(days=3),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name='default')

schedule = Schedule(
    name='schedule',
    onschedule_model='edc_visit_schedule.onschedule',
    offschedule_model='edc_visit_schedule.offschedule',
    appointment_model='edc_appointment.appointment',
    consent_model='edc_visit_schedule.subjectconsent')

schedule.add_visit(visit0)
schedule.add_visit(visit1)
schedule.add_visit(visit2)
schedule.add_visit(visit3)

visit_schedule = VisitSchedule(
    name='visit_schedule',
    offstudy_model='edc_visit_schedule.subjectoffstudy',
    death_report_model='edc_visit_schedule.deathreport')

visit_schedule.add_schedule(schedule)


visit_schedule2 = VisitSchedule(
    name='visit_schedule2',
    offstudy_model='edc_visit_schedule.subjectoffstudy2',
    death_report_model='edc_visit_schedule.deathreport')


schedule2 = Schedule(
    name='schedule2',
    onschedule_model='edc_visit_schedule.onschedule2',
    offschedule_model='edc_visit_schedule.offschedule2',
    appointment_model='edc_appointment.appointment',
    consent_model='edc_visit_schedule.subjectconsent')

schedule2.add_visit(visit3)

visit_schedule2.add_schedule(schedule2)
