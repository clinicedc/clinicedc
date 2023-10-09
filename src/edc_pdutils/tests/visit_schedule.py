from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.tests.dummy_panel import DummyPanel
from edc_visit_schedule.visit import Crf, FormsCollection, Requisition, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule


class Panel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model="edc_appointment.subjectrequisition", name=name)


def get_visit_schedule(i=None):
    i = i or 4

    crfs = FormsCollection(
        Crf(show_order=1, model="edc_metadata.crfone", required=True),
        Crf(show_order=2, model="edc_metadata.crftwo", required=True),
        Crf(show_order=3, model="edc_metadata.crfthree", required=True),
        Crf(show_order=4, model="edc_metadata.crffour", required=True),
        Crf(show_order=5, model="edc_metadata.crffive", required=True),
    )

    requisitions = FormsCollection(
        Requisition(show_order=10, panel=Panel("one"), required=True, additional=False),
        Requisition(show_order=20, panel=Panel("two"), required=True, additional=False),
        Requisition(show_order=30, panel=Panel("three"), required=True, additional=False),
        Requisition(show_order=40, panel=Panel("four"), required=True, additional=False),
        Requisition(show_order=50, panel=Panel("five"), required=True, additional=False),
        Requisition(show_order=60, panel=Panel("six"), required=True, additional=False),
    )

    visit_schedule = VisitSchedule(
        name="visit_schedule",
        offstudy_model="edc_offstudy.subjectoffstudy",
        death_report_model="edc_visit_tracking.deathreport",
        locator_model="edc_locator.subjectlocator",
    )

    schedule = Schedule(
        name="schedule",
        onschedule_model="edc_pdutils.onschedule",
        offschedule_model="edc_pdutils.offschedule",
        consent_model="edc_visit_tracking.subjectconsent",
        appointment_model="edc_appointment.appointment",
    )

    visits = []
    for index in range(0, i):
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
                facility_name="7-day-clinic",
                allow_unscheduled=True,
            )
        )
    for visit in visits:
        schedule.add_visit(visit)

    visit_schedule.add_schedule(schedule)
    return visit_schedule
