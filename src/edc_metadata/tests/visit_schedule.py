from dateutil.relativedelta import relativedelta

from edc_visit_schedule import VisitSchedule, Schedule, Visit
from edc_visit_schedule import FormsCollection, Crf, Requisition
from edc_visit_schedule.tests import DummyPanel


app_label = "edc_metadata"


class MockPanel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model="edc_metadata.subjectrequisition", name=name)


crfs_missed = FormsCollection(
    Crf(show_order=1, model="edc_metadata.subjectvisitmissed", required=True),
)

crfs0 = FormsCollection(
    Crf(show_order=1, model=f"{app_label}.crfone", required=True),
    Crf(show_order=2, model=f"{app_label}.crftwo", required=True),
    Crf(show_order=3, model=f"{app_label}.crfthree", required=True),
    Crf(show_order=4, model=f"{app_label}.crffour", required=True),
    Crf(show_order=5, model=f"{app_label}.crffive", required=True),
)

crfs1 = FormsCollection(
    Crf(show_order=1, model=f"{app_label}.crffour", required=True),
    Crf(show_order=2, model=f"{app_label}.crffive", required=True),
    Crf(show_order=3, model=f"{app_label}.crfsix", required=True),
)

crfs2 = FormsCollection(Crf(show_order=1, model=f"{app_label}.crfseven", required=True))


crfs_unscheduled = FormsCollection(
    Crf(show_order=1, model=f"{app_label}.crftwo", required=True),
    Crf(show_order=2, model=f"{app_label}.crfthree", required=True),
    Crf(show_order=3, model=f"{app_label}.crffive", required=True),
)

requisitions = FormsCollection(
    Requisition(show_order=10, panel=MockPanel("one"), required=True, additional=False),
    Requisition(show_order=20, panel=MockPanel("two"), required=True, additional=False),
    Requisition(
        show_order=30, panel=MockPanel("three"), required=True, additional=False
    ),
    Requisition(
        show_order=40, panel=MockPanel("four"), required=True, additional=False
    ),
    Requisition(
        show_order=50, panel=MockPanel("five"), required=True, additional=False
    ),
    Requisition(show_order=60, panel=MockPanel("six"), required=True, additional=False),
)

requisitions3000 = FormsCollection(
    Requisition(
        show_order=10, panel=MockPanel("seven"), required=True, additional=False
    )
)

requisitions_unscheduled = FormsCollection(
    Requisition(show_order=10, panel=MockPanel("one"), required=True, additional=False),
    Requisition(
        show_order=20, panel=MockPanel("three"), required=True, additional=False
    ),
    Requisition(
        show_order=30, panel=MockPanel("five"), required=True, additional=False
    ),
)

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
    crfs_missed=crfs_missed,
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
    onschedule_model="edc_metadata.onschedule",
    offschedule_model="edc_metadata.offschedule",
    consent_model="edc_metadata.subjectconsent",
    appointment_model="edc_appointment.appointment",
)

schedule.add_visit(visit0)
schedule.add_visit(visit1)
schedule.add_visit(visit2)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_metadata.subjectoffstudy",
    death_report_model="edc_metadata.deathreport",
)

visit_schedule.add_schedule(schedule)
