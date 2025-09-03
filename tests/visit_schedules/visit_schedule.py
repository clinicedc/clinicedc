from dateutil.relativedelta import relativedelta

from edc_consent.consent_definition import ConsentDefinition
from edc_lab_panel.panels import fbc_panel
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import (
    Crf,
    CrfCollection,
    Requisition,
    RequisitionCollection,
    Visit,
)
from edc_visit_schedule.visit_schedule import VisitSchedule


def get_visit_schedule(
    cdef: ConsentDefinition,
    crfs: CrfCollection = None,
    requisitions: RequisitionCollection = None,
    visit_schedule_name: str = None,
    schedule_name: str = None,
    onschedule_model: str = None,
    offschedule_model: str = None,
    visit_count: int = None,
    allow_unscheduled: bool = None,
):
    crfs = crfs or CrfCollection(
        Crf(show_order=1, model="tests.crflongitudinalone", required=True),
        Crf(show_order=2, model="tests.crflongitudinaltwo", required=True),
    )

    requisitions = requisitions or RequisitionCollection(
        Requisition(show_order=30, panel=fbc_panel, required=True, additional=False)
    )
    visit_schedule_name = visit_schedule_name or "visit_schedule"
    schedule_name = schedule_name or "schedule"
    onschedule_model = onschedule_model or "edc_visit_schedule.onschedule"
    offschedule_model = offschedule_model or "tests.offschedule"
    visit_count = visit_count or 2
    allow_unscheduled = True if allow_unscheduled is None else allow_unscheduled

    visits = []
    for index in range(0, visit_count):
        visits.append(
            Visit(
                code=f"{index + 1}000",
                title=f"Day {index + 1}",
                timepoint=index,
                rbase=relativedelta(months=index),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
                requisitions=requisitions,
                crfs=crfs,
                allow_unscheduled=allow_unscheduled,
            )
        )

    schedule = Schedule(
        name=schedule_name,
        onschedule_model=onschedule_model,
        offschedule_model=offschedule_model,
        consent_definitions=[cdef],
        appointment_model="edc_appointment.appointment",
    )

    for visit in visits:
        schedule.add_visit(visit)

    visit_schedule = VisitSchedule(
        name=visit_schedule_name,
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="edc_adverse_event.deathreport",
    )

    visit_schedule.add_schedule(schedule)
    return visit_schedule
