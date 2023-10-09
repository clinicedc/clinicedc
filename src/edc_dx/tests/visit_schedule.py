from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, FormsCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs_day1 = FormsCollection(
    Crf(show_order=1, model="dx_app.ClinicalReviewBaseline", required=True),
    Crf(show_order=10, model="dx_app.HivInitialReview", required=False),
    Crf(show_order=20, model="dx_app.HtnInitialReview", required=False),
    Crf(show_order=30, model="dx_app.DmInitialReview", required=False),
    Crf(show_order=40, model="dx_app.CholInitialReview", required=False),
)

crfs = FormsCollection(
    Crf(show_order=1, model="dx_app.ClinicalReview", required=True),
    Crf(show_order=10, model="dx_app.HivInitialReview", required=True),
    Crf(show_order=20, model="dx_app.HtnInitialReview", required=False),
    Crf(show_order=30, model="dx_app.DmInitialReview", required=False),
    Crf(show_order=40, model="dx_app.CholInitialReview", required=False),
    Crf(show_order=50, model="dx_app.HivReview", required=False),
    Crf(show_order=60, model="dx_app.HtnReview", required=False),
    Crf(show_order=70, model="dx_app.DmReview", required=False),
    Crf(show_order=80, model="dx_app.CholReview", required=False),
)

visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=None,
    # crfs=crfs_day1,
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
    # crfs=crfs,
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
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_metadata.deathreport",
)

visit_schedule.add_schedule(schedule)
