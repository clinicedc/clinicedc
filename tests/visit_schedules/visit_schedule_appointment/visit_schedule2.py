from dateutil.relativedelta import relativedelta

from edc_consent.consent_definition import ConsentDefinition
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule
from .crfs import crfs, crfs_missed, requisitions


def get_visit_schedule2(cdef: ConsentDefinition) -> VisitSchedule:
    visit_schedule2 = VisitSchedule(
        name="visit_schedule2",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="tests.deathreport",
    )

    schedule2 = Schedule(
        name="schedule2",
        onschedule_model="tests.onscheduletwo",
        offschedule_model="tests.offscheduletwo",
        appointment_model="edc_appointment.appointment",
        consent_definitions=[cdef],
        base_timepoint=4,
    )

    visits = []
    for index in range(4, 8):
        visits.append(
            Visit(
                code=f"{1 if index == 0 else index + 1}000",
                title=f"Day {1 if index == 0 else index + 1}",
                timepoint=index,
                rbase=relativedelta(days=7 * index),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
                requisitions=requisitions,
                crfs=crfs,
                crfs_missed=crfs_missed,
                facility_name="7-day-clinic",
            )
        )
    for visit in visits:
        schedule2.add_visit(visit)

    visit_schedule2.add_schedule(schedule2)
    return visit_schedule2
