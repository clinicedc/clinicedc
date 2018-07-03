from edc_appointment.tests.visit_schedule import visit_schedule1, visit_schedule2
# from edc_visit_schedule import FormsCollection, Crf, Requisition
# from edc_visit_schedule import VisitSchedule, Schedule, Visit
#
# from dateutil.relativedelta import relativedelta
#
#
# app_label = 'edc_offstudy'
#
# crfs = FormsCollection(
#     Crf(show_order=1, model=f'{app_label}.crfone', required=True),
# )
#
#
# visit0 = Visit(
#     code='1000',
#     title='Day 1',
#     timepoint=0,
#     rbase=relativedelta(days=0),
#     rlower=relativedelta(days=0),
#     rupper=relativedelta(days=6),
#     crfs=crfs)
#
# visit1 = Visit(
#     code='2000',
#     title='Day 2',
#     timepoint=1,
#     rbase=relativedelta(days=1),
#     rlower=relativedelta(days=0),
#     rupper=relativedelta(days=6),
#     crfs=crfs)
#
# visit2 = Visit(
#     code='3000',
#     title='Day 3',
#     timepoint=2,
#     rbase=relativedelta(days=2),
#     rlower=relativedelta(days=0),
#     rupper=relativedelta(days=6),
#     crfs=crfs)
#
# visit3 = Visit(
#     code='4000',
#     title='Day 4',
#     timepoint=3,
#     rbase=relativedelta(days=3),
#     rlower=relativedelta(days=0),
#     rupper=relativedelta(days=6),
#     crfs=crfs)
#
# schedule = Schedule(
#     name='schedule',
#     enrollment_model='edc_offstudy.enrollment',
#     disenrollment_model='edc_offstudy.disenrollment')
#
# schedule.add_visit(visit0)
# schedule.add_visit(visit1)
# schedule.add_visit(visit2)
# schedule.add_visit(visit3)
#
# visit_schedule = VisitSchedule(
#     name='visit_schedule',
#     visit_model='edc_offstudy.subjectvisit',
#     offstudy_model='edc_offstudy.subjectoffstudy')
#
# visit_schedule.add_schedule(schedule)
#
#
# visit_schedule2 = VisitSchedule(
#     name='visit_schedule2',
#     visit_model='edc_offstudy.subjectvisit',
#     offstudy_model='edc_offstudy.subjectoffstudy2')
#
#
# schedule2 = Schedule(
#     name='schedule2',
#     enrollment_model='edc_offstudy.enrollment2',
#     disenrollment_model='edc_offstudy.disenrollment2')
#
# schedule2.add_visit(visit3)
#
# visit_schedule2.add_schedule(schedule2)
