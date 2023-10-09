from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, FormsCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule

crfs = FormsCollection(
    Crf(show_order=1, model="edc_offstudy.crfone", required=True),
)


visit_schedule1 = VisitSchedule(
    name="visit_schedule1",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_adverse_event.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule1 = Schedule(
    name="schedule1",
    onschedule_model="edc_offstudy.onscheduleone",
    offschedule_model="edc_offstudy.offscheduleone",
    consent_model="edc_offstudy.subjectconsent",
    appointment_model="edc_appointment.appointment",
)


visits = []
for index in range(0, 4):
    visits.append(
        Visit(
            code=f"{index + 1}000",
            title=f"Day {index + 1}",
            timepoint=index,
            rbase=relativedelta(months=index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            requisitions=None,
            crfs=crfs,
            allow_unscheduled=True,
        )
    )
for visit in visits:
    schedule1.add_visit(visit)


visit_schedule1.add_schedule(schedule1)
