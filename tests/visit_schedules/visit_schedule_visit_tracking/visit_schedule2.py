from dateutil.relativedelta import relativedelta

from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.tests.dummy_panel import DummyPanel
from edc_visit_schedule.visit import (
    Crf,
    CrfCollection,
    Requisition,
    RequisitionCollection,
    Visit,
)
from edc_visit_schedule.visit_schedule import VisitSchedule


class Panel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model="tests.subjectrequisition", name=name)


crfs = CrfCollection(
    Crf(show_order=1, model="tests.crfone", required=True),
    Crf(show_order=2, model="tests.crftwo", required=True),
    Crf(show_order=3, model="tests.crfthree", required=True),
    Crf(show_order=4, model="tests.crffour", required=True),
    Crf(show_order=5, model="tests.crffive", required=True),
)

requisitions = RequisitionCollection(
    Requisition(show_order=10, panel=Panel("one"), required=True, additional=False),
    Requisition(show_order=20, panel=Panel("two"), required=True, additional=False),
    Requisition(show_order=30, panel=Panel("three"), required=True, additional=False),
    Requisition(show_order=40, panel=Panel("four"), required=True, additional=False),
    Requisition(show_order=50, panel=Panel("five"), required=True, additional=False),
    Requisition(show_order=60, panel=Panel("six"), required=True, additional=False),
)


def get_visit_schedule(cdef):
    visit_schedule = VisitSchedule(
        name="visit_schedule2",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="tests.deathreport",
        locator_model="edc_locator.subjectlocator",
    )

    schedule = Schedule(
        name="schedule2",
        onschedule_model="tests.onscheduletwo",
        offschedule_model="tests.offscheduletwo",
        consent_definitions=[cdef],
        base_timepoint=4,
    )

    visits = []
    for index in range(4, 8):
        visits.append(
            Visit(
                code=f"{index + 1}000",
                title=f"Day {index + 1}",
                timepoint=index,
                rbase=relativedelta(days=index),
                rlower=relativedelta(days=0),
                rupper=relativedelta(days=6),
                requisitions=requisitions,
                crfs=crfs,
            )
        )
    for visit in visits:
        schedule.add_visit(visit)

    visit_schedule.add_schedule(schedule)

    return visit_schedule
