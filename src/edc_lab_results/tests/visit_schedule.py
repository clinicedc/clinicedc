from dateutil.relativedelta import relativedelta
from edc_lab_panel.panels import (
    blood_glucose_panel,
    fbc_panel,
    hba1c_panel,
    lft_panel,
    lipids_panel,
    rft_panel,
)
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, FormsCollection, Requisition, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs = FormsCollection(
    Crf(show_order=1, model="edc_lab_results.BloodResultsFbc", required=True),
)

requisitions = FormsCollection(
    Requisition(show_order=10, panel=fbc_panel, required=True, additional=False),
    Requisition(show_order=20, panel=lft_panel, required=True, additional=False),
    Requisition(show_order=30, panel=rft_panel, required=False, additional=False),
    Requisition(show_order=40, panel=lipids_panel, required=False, additional=False),
    Requisition(show_order=50, panel=blood_glucose_panel, required=False, additional=False),
    Requisition(show_order=60, panel=hba1c_panel, required=False, additional=False),
)


visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=requisitions,
    crfs=crfs,
    crfs_unscheduled=None,
    requisitions_unscheduled=None,
    facility_name="7-day-clinic",
)

visit1 = Visit(
    code="2000",
    title="Day 2",
    timepoint=1,
    rbase=relativedelta(days=1),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=requisitions,
    crfs=crfs,
    crfs_unscheduled=None,
    requisitions_unscheduled=None,
    facility_name="7-day-clinic",
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

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_metadata.deathreport",
)

visit_schedule.add_schedule(schedule)
