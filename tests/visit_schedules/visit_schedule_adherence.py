from dateutil.relativedelta import relativedelta

from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, CrfCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule
from tests.consents import consent_v1

crfs = CrfCollection(
    Crf(show_order=1, model="tests.medicationadherence", required=True)
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


schedule_adherence = Schedule(
    name="schedule_adherence",
    onschedule_model="edc_visit_schedule.onschedule",
    offschedule_model="tests.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent_v1],
)

visit_schedule_adherence = VisitSchedule(
    name="visit_schedule_adherence",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_adverse_event.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule_adherence.add_visit(visit)

visit_schedule_adherence.add_schedule(schedule_adherence)
