from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, FormsCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs = FormsCollection(
    Crf(show_order=1, model="edc_timepoint.crfone", required=True),
    Crf(show_order=2, model="edc_timepoint.crftwo", required=True),
)


visit_schedule1 = VisitSchedule(
    name="visit_schedule1",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_timepoint.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule1 = Schedule(
    name="schedule1",
    onschedule_model="edc_timepoint.onschedule",
    offschedule_model="edc_timepoint.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_timepoint.subjectconsent",
)

visits = []
for index in range(0, 4):
    visits.append(
        Visit(
            code=f"{index + 1}000",
            title=f"Day {index + 1}",
            timepoint=index,
            rbase=relativedelta(days=index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            crfs=crfs,
            allow_unscheduled=True,
            facility_name="5-day-clinic",
        )
    )
for visit in visits:
    schedule1.add_visit(visit)

visit_schedule1.add_schedule(schedule1)
