from dateutil.relativedelta import relativedelta
from edc_visit_schedule import Crf, FormsCollection, Schedule, Visit, VisitSchedule
from edc_visit_schedule.tests.dummy_panel import DummyPanel
from edc_visit_schedule.visit.requisition import Requisition


class MockPanel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model="edc_lab.subjectrequisition", name=name)


crfs = FormsCollection(Crf(show_order=1, model="edc_lab.crfone", required=True))

requisitions = FormsCollection(
    Requisition(show_order=10, panel=MockPanel("panel"), required=True, additional=False)
)


visit = Visit(
    code="1000",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=requisitions,
    crfs=crfs,
    requisitions_unscheduled=None,
    crfs_unscheduled=None,
    allow_unscheduled=False,
    facility_name="5-day-clinic",
)


schedule = Schedule(
    name="schedule",
    onschedule_model="edc_lab.onschedule",
    offschedule_model="edc_lab.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_lab.subjectconsent",
)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_appointment.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule.add_visit(visit)

visit_schedule.add_schedule(schedule)
