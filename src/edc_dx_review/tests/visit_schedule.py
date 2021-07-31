from dateutil.relativedelta import relativedelta
from edc_visit_schedule import Crf, FormsCollection, Schedule, Visit, VisitSchedule

crfs_day1 = FormsCollection(
    Crf(show_order=1, model="edc_dx_review.ClinicalReviewBaseline", required=True),
)

crfs = FormsCollection(
    Crf(show_order=1, model="edc_dx_review.ClinicalReview", required=True),
)

visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=None,
    crfs=crfs_day1,
    crfs_unscheduled=None,
    requisitions_unscheduled=None,
    facility_name="7-day-clinic",
)

visit1 = Visit(
    code="1010",
    title="Month 1",
    timepoint=1,
    rbase=relativedelta(days=30),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=None,
    crfs=crfs,
    crfs_unscheduled=None,
    requisitions_unscheduled=None,
    facility_name="7-day-clinic",
)


schedule = Schedule(
    name="schedule",
    onschedule_model="edc_metadata.onschedule",
    offschedule_model="edc_metadata.offschedule",
    consent_model="edc_metadata.subjectconsent",
    appointment_model="edc_appointment.appointment",
)

schedule.add_visit(visit0)
schedule.add_visit(visit1)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_metadata.subjectoffstudy",
    death_report_model="edc_metadata.deathreport",
)

visit_schedule.add_schedule(schedule)
