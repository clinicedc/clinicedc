from dateutil.relativedelta import relativedelta
from edc_visit_schedule import VisitSchedule, Schedule, Visit
from edc_visit_schedule import FormsCollection, Crf

crfs = FormsCollection(
    Crf(show_order=1, model='edc_metadata.crfone', required=True),
    Crf(show_order=2, model='edc_metadata.crftwo', required=True),
)


visit_schedule1 = VisitSchedule(
    name='visit_schedule1',
    offstudy_model='edc_offstudy.subjectoffstudy',
    death_report_model='edc_appointment.deathreport',
    locator_model='edc_appointment.subjectlocator')

schedule1 = Schedule(
    name='schedule1',
    onschedule_model='edc_appointment.onscheduleone',
    offschedule_model='edc_appointment.offscheduleone',
    appointment_model='edc_appointment.appointment',
    consent_model='edc_appointment.subjectconsent')

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
            crfs=crfs,
            allow_unscheduled=True,
            facility_name='5-day-clinic'))
for visit in visits:
    schedule1.add_visit(visit)

visit_schedule1.add_schedule(schedule1)
