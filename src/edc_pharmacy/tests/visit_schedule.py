from dateutil.relativedelta import relativedelta
from edc_consent.utils import get_consent_model_name
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, FormsCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

app_label = "edc_pharmacy"

crfs = FormsCollection(
    Crf(show_order=1, model=f"{app_label}.studymedication", required=True),
)

visit0 = Visit(
    code="1000",
    title="Week 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    allow_unscheduled=True,
    facility_name="5-day-clinic",
)

visit1 = Visit(
    code="2000",
    title="Week 2",
    timepoint=1,
    rbase=relativedelta(days=7),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name="5-day-clinic",
    allow_unscheduled=True,
)

visit2 = Visit(
    code="3000",
    title="Week 3",
    timepoint=2,
    rbase=relativedelta(days=14),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
    facility_name="5-day-clinic",
)

schedule = Schedule(
    name="schedule",
    onschedule_model="edc_pharmacy.onschedule",
    offschedule_model="edc_pharmacy.offschedule",
    consent_model=get_consent_model_name(),
    appointment_model="edc_appointment.appointment",
)

schedule.add_visit(visit0)
schedule.add_visit(visit1)
schedule.add_visit(visit2)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_adverse_event.deathreport",
)

visit_schedule.add_schedule(schedule)
