from __future__ import annotations

from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta

from edc_visit_schedule.constants import MONTH0, MONTH1, MONTH2, MONTH3, MONTH4
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, CrfCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

from ...consents import consent_v1

if TYPE_CHECKING:
    from edc_consent.consent_definition import ConsentDefinition


def get_visit_schedule6(cdef: ConsentDefinition | None = None) -> VisitSchedule:
    app_label = "tests"

    cdef = cdef or consent_v1

    crfs = CrfCollection(
        Crf(show_order=1, model=f"{app_label}.nextappointmentcrf", required=True),
    )

    visit0 = Visit(
        code=MONTH0,
        title=MONTH0,
        timepoint=0,
        rbase=relativedelta(days=0),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        crfs=crfs,
        facility_name="5-day-clinic",
    )

    visit1 = Visit(
        code=MONTH1,
        title=MONTH1,
        timepoint=1,
        rbase=relativedelta(months=1),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        crfs=crfs,
        facility_name="5-day-clinic",
    )

    visit2 = Visit(
        code=MONTH2,
        title=MONTH2,
        timepoint=2,
        rbase=relativedelta(months=2),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        crfs=crfs,
        facility_name="5-day-clinic",
        allow_unscheduled=True,
    )

    visit3 = Visit(
        code=MONTH3,
        title=MONTH3,
        timepoint=3,
        rbase=relativedelta(months=3),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        crfs=crfs,
        facility_name="5-day-clinic",
    )

    visit4 = Visit(
        code=MONTH4,
        title=MONTH4,
        timepoint=4,
        rbase=relativedelta(months=4),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        crfs=crfs,
        facility_name="5-day-clinic",
    )

    schedule = Schedule(
        name="schedule6",
        onschedule_model=f"{app_label}.onschedulesix",
        offschedule_model=f"{app_label}.offschedulesix",
        consent_definitions=[cdef],
        appointment_model="edc_appointment.appointment",
    )

    schedule.add_visit(visit0)
    schedule.add_visit(visit1)
    schedule.add_visit(visit2)
    schedule.add_visit(visit3)
    schedule.add_visit(visit4)

    visit_schedule6 = VisitSchedule(
        name="visit_schedule6",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model=f"{app_label}.deathreport",
    )

    visit_schedule6.add_schedule(schedule)
    return visit_schedule6
