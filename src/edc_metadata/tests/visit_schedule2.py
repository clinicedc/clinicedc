from dateutil.relativedelta import relativedelta
from edc_visit_schedule import Crf, FormsCollection, Schedule, Visit, VisitSchedule
from edc_visit_schedule.constants import DAY1, MONTH1, MONTH3, MONTH6, WEEK2
from edc_visit_schedule.tests import DummyPanel

app_label = "edc_metadata"


class MockPanel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model="edc_metadata.subjectrequisition", name=name)


crfs_prn = FormsCollection(
    Crf(show_order=100, model=f"{app_label}.prnone"),
    Crf(show_order=200, model=f"{app_label}.prntwo"),
)

crfs_missed = FormsCollection(
    Crf(show_order=1, model="edc_metadata.subjectvisitmissed", required=True),
)

crfs0 = FormsCollection(Crf(show_order=1, model=f"{app_label}.crftwo", required=False))
crfs1 = FormsCollection(Crf(show_order=1, model=f"{app_label}.crfone", required=True))
crfs2 = FormsCollection(Crf(show_order=1, model=f"{app_label}.crfone", required=False))
crfs3 = FormsCollection(Crf(show_order=1, model=f"{app_label}.crfone", required=False))
crfs4 = FormsCollection(Crf(show_order=1, model=f"{app_label}.crfone", required=False))


visit0 = Visit(
    code=DAY1,
    title="Week 1",
    timepoint=0.0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs0,
    crfs_prn=crfs_prn,
    allow_unscheduled=True,
    facility_name="5-day-clinic",
)

visit1 = Visit(
    code=WEEK2,
    title="Week 2",
    timepoint=1.0,
    rbase=relativedelta(days=7),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs1,
    crfs_prn=crfs_prn,
    crfs_missed=crfs_missed,
    facility_name="5-day-clinic",
)

visit2 = Visit(
    code=MONTH1,
    title="Month 1",
    timepoint=2.0,
    rbase=relativedelta(months=1),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs2,
    crfs_prn=crfs_prn,
    facility_name="5-day-clinic",
)

visit3 = Visit(
    code=MONTH3,
    title="Month 3",
    timepoint=3.0,
    rbase=relativedelta(months=3),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs3,
    crfs_prn=crfs_prn,
    facility_name="5-day-clinic",
)

visit4 = Visit(
    code=MONTH6,
    title="Month 6",
    timepoint=4.0,
    rbase=relativedelta(months=6),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs4,
    crfs_prn=crfs_prn,
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
schedule.add_visit(visit3)
schedule.add_visit(visit4)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_metadata.deathreport",
)

visit_schedule.add_schedule(schedule)
