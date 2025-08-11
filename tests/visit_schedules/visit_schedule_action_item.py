from dateutil.relativedelta import relativedelta

from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, CrfCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs = CrfCollection(
    Crf(show_order=1, model="tests.crflongitudinalone", required=True),
    Crf(show_order=2, model="tests.crflongitudinaltwo", required=True),
)

visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=None,
    crfs=crfs,
    crfs_unscheduled=None,
    requisitions_unscheduled=None,
    facility_name="7-day-clinic",
)

visit1 = Visit(
    code="2000",
    title="Day 2",
    timepoint=1,
    rbase=relativedelta(days=1),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=None,
    crfs=crfs,
    crfs_unscheduled=None,
    requisitions_unscheduled=None,
    facility_name="7-day-clinic",
)


def get_visit_schedule(cdef):
    schedule_action_item = Schedule(
        name="schedule_action_item",
        onschedule_model="edc_visit_schedule.onschedule",
        offschedule_model="tests.offschedule",
        consent_definitions=[cdef],
        appointment_model="edc_appointment.appointment",
    )

    schedule_action_item.add_visit(visit0)
    schedule_action_item.add_visit(visit1)

    visit_schedule_action_item = VisitSchedule(
        name="visit_schedule_action_item",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="edc_adverse_event.deathreport",
    )

    visit_schedule_action_item.add_schedule(schedule_action_item)
    return visit_schedule_action_item
