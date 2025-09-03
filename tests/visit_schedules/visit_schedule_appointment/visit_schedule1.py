from dateutil.relativedelta import relativedelta

from edc_consent.consent_definition import ConsentDefinition
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule
from .crfs import crfs, crfs_missed, crfs_unscheduled, requisitions


def get_visit_schedule1(cdef: ConsentDefinition) -> VisitSchedule:
    visit_schedule1 = VisitSchedule(
        name="visit_schedule1",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="tests.deathreport",
    )

    schedule1 = Schedule(
        name="schedule1",
        onschedule_model="tests.onscheduleone",
        offschedule_model="tests.offscheduleone",
        appointment_model="edc_appointment.appointment",
        consent_definitions=[cdef],
    )

    visits = []
    for index in range(0, 4):
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
                requisitions_unscheduled=requisitions,
                crfs_unscheduled=crfs_unscheduled,
                allow_unscheduled=True,
                facility_name="5-day-clinic",
            )
        )
    for visit in visits:
        schedule1.add_visit(visit)
    visit_schedule1.add_schedule(schedule1)
    return visit_schedule1
