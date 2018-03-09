from dateutil.relativedelta import relativedelta

from edc_visit_schedule import VisitSchedule, Schedule, Visit
from edc_visit_schedule import FormsCollection, Crf, Requisition, Panel


panel_one = Panel(
    name='one', requisition_model='edc_metadata.subjectrequisition')
panel_two = Panel(
    name='two', requisition_model='edc_metadata.subjectrequisition')
panel_three = Panel(
    name='three', requisition_model='edc_metadata.subjectrequisition')
panel_four = Panel(
    name='four', requisition_model='edc_metadata.subjectrequisition')
panel_five = Panel(
    name='five', requisition_model='edc_metadata.subjectrequisition')
panel_six = Panel(
    name='six', requisition_model='edc_metadata.subjectrequisition')

crfs = FormsCollection(
    Crf(show_order=1, model='edc_metadata.crfone', required=True),
    Crf(show_order=2, model='edc_metadata.crftwo', required=True),
    Crf(show_order=3, model='edc_metadata.crfthree', required=True),
    Crf(show_order=4, model='edc_metadata.crffour', required=True),
    Crf(show_order=5, model='edc_metadata.crffive', required=True),
)

requisitions = FormsCollection(
    Requisition(
        show_order=10,
        panel=panel_one, required=True, additional=False),
    Requisition(
        show_order=20,
        panel=panel_two, required=True, additional=False),
    Requisition(
        show_order=30,
        panel=panel_three, required=True, additional=False),
    Requisition(
        show_order=40,
        panel=panel_four, required=True, additional=False),
    Requisition(
        show_order=50,
        panel=panel_five, required=True, additional=False),
    Requisition(
        show_order=60,
        panel=panel_six, required=True, additional=False),
)


crfs_unscheduled = FormsCollection(
    Crf(show_order=1, model='edc_metadata.crfone', required=True),
    Crf(show_order=3, model='edc_metadata.crfthree', required=True),
    Crf(show_order=5, model='edc_metadata.crffive', required=True),
)


visit_schedule1 = VisitSchedule(
    name='visit_schedule1',
    offstudy_model='edc_appointment.subjectoffstudy',
    death_report_model='edc_appointment.deathreport')

visit_schedule2 = VisitSchedule(
    name='visit_schedule2',
    offstudy_model='edc_appointment.subjectoffstudy',
    death_report_model='edc_appointment.deathreport')

schedule1 = Schedule(
    name='schedule1',
    onschedule_model='edc_appointment.onscheduleone',
    offschedule_model='edc_appointment.offscheduleone',
    appointment_model='edc_appointment.appointment',
    consent_model='edc_appointment.subjectconsent')

schedule2 = Schedule(
    name='schedule2',
    onschedule_model='edc_appointment.onscheduletwo',
    offschedule_model='edc_appointment.offscheduletwo',
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
            requisitions=requisitions,
            crfs=crfs,
            requisitions_unscheduled=requisitions,
            crfs_unscheduled=crfs_unscheduled,
            allow_unscheduled=True,
            facility_name='5-day-clinic'))
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
            crfs=crfs,
            facility_name='7-day-clinic'))
for visit in visits:
    schedule2.add_visit(visit)

visit_schedule1.add_schedule(schedule1)
visit_schedule2.add_schedule(schedule2)
