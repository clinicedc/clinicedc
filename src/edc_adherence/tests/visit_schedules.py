from dateutil.relativedelta import relativedelta
from edc_visit_schedule import Crf, FormsCollection, Schedule, Visit, VisitSchedule

crfs = FormsCollection(
    Crf(show_order=1, model="edc_adherence.medicationadherence", required=True)
)

visit = Visit(
    code="1000",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=None,
    crfs=crfs,
    requisitions_unscheduled=None,
    crfs_unscheduled=None,
    allow_unscheduled=False,
    facility_name="5-day-clinic",
)


schedule = Schedule(
    name="schedule",
    onschedule_model="edc_adherence.onschedule",
    offschedule_model="edc_adherence.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_adherence.subjectconsent",
)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_adherence.offstudy",
    death_report_model="edc_adherence.deathreport",
    locator_model="edc_adherence.locator",
)

schedule.add_visit(visit)

visit_schedule.add_schedule(schedule)
