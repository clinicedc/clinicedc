from dateutil.relativedelta import relativedelta

from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.visit import Crf, CrfCollection, Visit
from edc_visit_schedule.visit_schedule import VisitSchedule
from ...consents import consent2_v1, consent5_v1, consent6_v1, consent7_v1, consent_v1

crfs = CrfCollection(Crf(show_order=1, model="tests.crfone", required=True))

visit0 = Visit(
    code="1000",
    title="Day 1",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
)

visit1 = Visit(
    code="2000",
    title="Day 2",
    timepoint=1,
    rbase=relativedelta(days=1),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
)

visit2 = Visit(
    code="3000",
    title="Day 3",
    timepoint=2,
    rbase=relativedelta(days=2),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
)

visit3 = Visit(
    code="4000",
    title="Day 4",
    timepoint=3,
    rbase=relativedelta(days=3),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    crfs=crfs,
)

schedule = Schedule(
    name="schedule",
    onschedule_model="edc_visit_schedule.onschedule",
    offschedule_model="edc_visit_schedule.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent_v1],
)

schedule.add_visit(visit0)
schedule.add_visit(visit1)
schedule.add_visit(visit2)
schedule.add_visit(visit3)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="tests.deathreport",
)

visit_schedule.add_schedule(schedule)

# visit_schedule2
schedule2 = Schedule(
    name="schedule_two",
    onschedule_model="tests.onscheduletwo",
    offschedule_model="tests.offscheduletwo",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent2_v1],
    base_timepoint=3,
)

schedule2.add_visit(visit3)
schedule4 = Schedule(
    name="schedule_four",
    onschedule_model="tests.onschedulefour",
    offschedule_model="tests.offschedulefour",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent2_v1],
    base_timepoint=3,
)

schedule4.add_visit(visit3)
visit_schedule2 = VisitSchedule(
    name="visit_schedule_two",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="tests.deathreport",
)

visit_schedule2.add_schedule(schedule2)
visit_schedule2.add_schedule(schedule4)

# visit_schedule5
schedule5 = Schedule(
    name="schedule5",
    onschedule_model="tests.onschedulefive",
    offschedule_model="tests.offschedulefive",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent5_v1],
)

schedule5.add_visit(visit0)
visit_schedule5 = VisitSchedule(
    name="visit_schedule5",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="tests.deathreport",
)

visit_schedule5.add_schedule(schedule5)

# visit_schedule6
schedule6 = Schedule(
    name="schedule6",
    onschedule_model="tests.onschedulesix",
    offschedule_model="tests.offschedulesix",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent6_v1],
)

schedule6.add_visit(visit0)
visit_schedule6 = VisitSchedule(
    name="visit_schedule6",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="tests.deathreport",
)

visit_schedule6.add_schedule(schedule6)

# visit_schedule7
schedule7 = Schedule(
    name="schedule7",
    onschedule_model="tests.onscheduleseven",
    offschedule_model="tests.offscheduleseven",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent7_v1],
)

schedule7.add_visit(visit0)
visit_schedule7 = VisitSchedule(
    name="visit_schedule7",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="tests.deathreport",
)

visit_schedule7.add_schedule(schedule7)
