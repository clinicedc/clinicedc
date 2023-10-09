from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, FormsCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs = FormsCollection(Crf(show_order=1, model="edc_form_label.mymodel", required=True))


visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name="7-day-clinic",
)

visit1 = Visit(
    code="2000",
    title="Day 2",
    timepoint=1,
    rbase=relativedelta(days=1),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name="7-day-clinic",
)

schedule = Schedule(
    name="schedule",
    onschedule_model="edc_form_label.onschedule",
    offschedule_model="edc_form_label.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_consent.subjectconsent",
)

schedule.add_visit(visit0)
schedule.add_visit(visit1)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_adverse_event.deathreport",
)

visit_schedule.add_schedule(schedule)
