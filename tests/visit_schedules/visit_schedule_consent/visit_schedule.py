from __future__ import annotations

from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta

from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, CrfCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

if TYPE_CHECKING:
    from edc_consent.consent_definition import ConsentDefinition


def get_visit_schedule(
    consent_definition: ConsentDefinition | list[ConsentDefinition],
    extend: bool | None = None,
) -> VisitSchedule:
    crfs = CrfCollection(
        Crf(show_order=10, model="tests.crfone", required=True),
        Crf(show_order=20, model="tests.crfeight", required=True),
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

    visit1010 = Visit(
        code="1010",
        timepoint=1,
        rbase=relativedelta(months=1),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=None,
        crfs=crfs,
        requisitions_unscheduled=None,
        crfs_unscheduled=None,
        allow_unscheduled=False,
        facility_name="5-day-clinic",
    )

    visit1020 = Visit(
        code="1020",
        timepoint=2,
        rbase=relativedelta(months=2),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=None,
        crfs=crfs,
        requisitions_unscheduled=None,
        crfs_unscheduled=None,
        allow_unscheduled=False,
        facility_name="5-day-clinic",
    )

    visit1030 = Visit(
        code="1030",
        timepoint=3,
        rbase=relativedelta(months=3),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=None,
        crfs=crfs,
        requisitions_unscheduled=None,
        crfs_unscheduled=None,
        allow_unscheduled=False,
        facility_name="5-day-clinic",
    )

    visit1040 = Visit(
        code="1040",
        timepoint=4,
        rbase=relativedelta(months=4),
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
        name="schedule1",
        onschedule_model="tests.onscheduleone",
        offschedule_model="tests.offscheduleone",
        appointment_model="edc_appointment.appointment",
        consent_definitions=consent_definition,
    )

    visit_schedule = VisitSchedule(
        name="visit_schedule",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="tests.deathreport",
        locator_model="edc_locator.subjectlocator",
    )

    schedule.add_visit(visit)
    if extend:
        schedule.add_visit(visit1010)
        schedule.add_visit(visit1020)
        schedule.add_visit(visit1030)
        schedule.add_visit(visit1040)

    visit_schedule.add_schedule(schedule)
    return visit_schedule
