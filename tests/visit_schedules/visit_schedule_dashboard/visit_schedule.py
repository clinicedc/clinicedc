from dateutil.relativedelta import relativedelta

from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.tests import DummyPanel
from edc_visit_schedule.visit import (
    Crf,
    CrfCollection,
    Requisition,
    RequisitionCollection,
    Visit,
)
from edc_visit_schedule.visit_schedule import VisitSchedule

from .lab_profiles import panel_one, panel_two

app_label = "tests"


class MockPanel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model=f"{app_label}.subjectrequisition", name=name)


crfs0 = CrfCollection(
    Crf(show_order=1, model=f"{app_label}.crfone", required=True),
    Crf(show_order=2, model=f"{app_label}.crftwo", required=True),
    Crf(show_order=3, model=f"{app_label}.crfthree", required=True),
    Crf(show_order=4, model=f"{app_label}.crffour", required=True),
    Crf(show_order=5, model=f"{app_label}.crffive", required=True),
)

crfs1 = CrfCollection(
    Crf(show_order=1, model=f"{app_label}.crfone", required=True),
    Crf(show_order=2, model=f"{app_label}.crffour", required=True),
    Crf(show_order=3, model=f"{app_label}.crffive", required=True),
    Crf(show_order=4, model=f"{app_label}.crfsix", required=True),
)

crfs2 = CrfCollection(Crf(show_order=1, model=f"{app_label}.crfseven", required=True))


crfs_unscheduled = CrfCollection(
    Crf(show_order=10, model=f"{app_label}.crfone", required=True),
    Crf(show_order=20, model=f"{app_label}.crftwo", required=True),
    Crf(show_order=30, model=f"{app_label}.crfthree", required=True),
    Crf(show_order=40, model=f"{app_label}.crffive", required=True),
)

requisitions = RequisitionCollection(
    Requisition(show_order=10, panel=panel_one, required=True, additional=False),
    Requisition(show_order=20, panel=panel_two, required=True, additional=False),
)

requisitions3000 = RequisitionCollection(
    Requisition(
        show_order=10, panel=MockPanel("seven"), required=True, additional=False
    )
)

requisitions_unscheduled = RequisitionCollection(
    Requisition(
        show_order=105, panel=MockPanel("one"), required=True, additional=False
    ),
    Requisition(
        show_order=205, panel=MockPanel("three"), required=True, additional=False
    ),
    Requisition(
        show_order=305, panel=MockPanel("five"), required=True, additional=False
    ),
)


def get_visit_schedule(cdef):
    visit0 = Visit(
        code="1000",
        title="Day 1",
        timepoint=0,
        rbase=relativedelta(days=0),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=requisitions,
        crfs=crfs0,
        crfs_unscheduled=crfs_unscheduled,
        requisitions_unscheduled=requisitions_unscheduled,
        allow_unscheduled=True,
        facility_name="5-day-clinic",
    )

    visit1 = Visit(
        code="2000",
        title="Day 2",
        timepoint=1,
        rbase=relativedelta(days=1),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=requisitions,
        crfs=crfs1,
        facility_name="5-day-clinic",
    )

    visit2 = Visit(
        code="3000",
        title="Day 3",
        timepoint=2,
        rbase=relativedelta(days=2),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=6),
        requisitions=requisitions3000,
        crfs=crfs2,
        facility_name="5-day-clinic",
    )

    schedule = Schedule(
        name="schedule",
        onschedule_model="edc_visit_schedule.onschedule",
        offschedule_model=f"{app_label}.offschedule",
        consent_definitions=[cdef],
        appointment_model="edc_appointment.appointment",
    )

    schedule.add_visit(visit0)
    schedule.add_visit(visit1)
    schedule.add_visit(visit2)

    visit_schedule = VisitSchedule(
        name="visit_schedule",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model=f"{app_label}.deathreport",
    )

    visit_schedule.add_schedule(schedule)
    return visit_schedule
