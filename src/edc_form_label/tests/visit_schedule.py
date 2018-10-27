from edc_visit_schedule import Schedule, VisitSchedule, FormsCollection, Crf, Visit

from dateutil.relativedelta import relativedelta


crfs = FormsCollection(
    Crf(show_order=1, model=f'edc_fieldsets.mymodel', required=True),
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

schedule = Schedule(
    name='schedule',
    onschedule_model='edc_visit_schedule.onschedule',
    offschedule_model='edc_visit_schedule.offschedule',
    appointment_model='edc_appointment.appointment',
    consent_model='edc_visit_schedule.subjectconsent')

schedule.add_visit(visit0)
schedule.add_visit(visit1)

visit_schedule = VisitSchedule(
    name='visit_schedule',
    offstudy_model='edc_visit_schedule.subjectoffstudy',
    death_report_model='edc_visit_schedule.deathreport')

visit_schedule.add_schedule(schedule)
