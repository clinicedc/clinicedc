from dateutil.relativedelta import relativedelta

from edc_consent.consent_definition import ConsentDefinition
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

from ...consents import consent_v1
from .crfs import crfs, crfs_missed, requisitions


def get_visit_schedule3(cdef: ConsentDefinition | None = None) -> VisitSchedule:
    visit_schedule3 = VisitSchedule(
        name="visit_schedule3",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="tests.deathreport",
    )

    schedule3 = Schedule(
        name="three_monthly_schedule",
        onschedule_model="tests.onschedulethree",
        offschedule_model="tests.offschedulethree",
        appointment_model="edc_appointment.appointment",
        consent_definitions=[cdef or consent_v1],
    )

    visits = [
        Visit(
            code="1000",
            title="Baseline",
            timepoint=0,
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=0),
            requisitions=requisitions,
            crfs=crfs,
            crfs_missed=crfs_missed,
            facility_name="7-day-clinic",
        )
    ]
    for index, visit_code in [(3, "1030"), (6, "1060"), (9, "1090"), (12, "1120")]:
        visits.append(
            Visit(
                code=visit_code,
                title=f"Month {index}",
                timepoint=index,
                rbase=relativedelta(months=index),
                rlower=relativedelta(days=14),
                rupper=relativedelta(days=45),
                requisitions=requisitions,
                crfs=crfs,
                crfs_missed=crfs_missed,
                facility_name="7-day-clinic",
                allow_unscheduled=True,
            )
        )
    for visit in visits:
        schedule3.add_visit(visit)

    visit_schedule3.add_schedule(schedule3)
    return visit_schedule3
