from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, FormsCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs = FormsCollection(Crf(show_order=1, model="edc_crf.crf", required=True))

visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
)

visit1 = Visit(
    code="2000",
    title="Day 2",
    timepoint=1,
    rbase=relativedelta(days=1),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
)

visit2 = Visit(
    code="3000",
    title="Day 3",
    timepoint=2,
    rbase=relativedelta(days=2),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
)

visit3 = Visit(
    code="4000",
    title="Day 4",
    timepoint=3,
    rbase=relativedelta(days=3),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
)

schedule = Schedule(
    name="schedule",
    onschedule_model="visit_schedule_app.onschedule",
    offschedule_model="visit_schedule_app.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_model="visit_schedule_app.subjectconsent",
)

schedule.add_visit(visit0)
schedule.add_visit(visit1)
schedule.add_visit(visit2)
schedule.add_visit(visit3)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_protocol_incident.deathreport",
)

visit_schedule.add_schedule(schedule)
