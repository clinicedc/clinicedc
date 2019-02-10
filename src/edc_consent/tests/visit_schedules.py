from dateutil.relativedelta import relativedelta

from edc_visit_schedule import VisitSchedule, Schedule, Visit
from edc_visit_schedule import FormsCollection, Crf


crfs = FormsCollection(Crf(show_order=1, model="edc_consent.crfone", required=True))

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


schedule = Schedule(
    name="schedule1",
    onschedule_model="edc_appointment.onscheduleone",
    offschedule_model="edc_appointment.offscheduleone",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_consent.subjectconsent",
)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_appointment.subjectoffstudy",
    death_report_model="edc_appointment.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule.add_visit(visit)

visit_schedule.add_schedule(schedule)
