# from edc_visit_schedule.site_visit_schedules import site_visit_schedules
#
# from .rule import Rule
#
#
# class VisitScheduleRule(Rule):
#
#     visit_schedule_name = None
#     schedule_name = None
#     visit_codes = None
#
#     def __init__(self, visit_schedule_name=None, schedule_name=None,
#                  visit_codes=None, **kwargs):
#         super().__init__(**kwargs)
#         self.schedule = None
#         self.visits = None
#         self.visit_schedule_name = visit_schedule_name or self.visit_schedule_name
#         self.visit_schedule = site_visit_schedules.get_visit_schedule(
#             self.visit_schedule_name)
#         if self.visit_schedule:
#             self.schedule = self.visit_schedule.schedules.get(
#                 schedule_name or self.schedule_name)
#             if self.schedule:
#                 if visit_codes:
#                     self.visits = (
#                         v for v in self.schedule.visits
#                         if v.visit_code in visit_codes or self.visit_codes or [])
#             else:
#                 # get all schedules and visits
#                 if self.visits:
#                     pass
#         else:
#             # get all schedules, all visits
#             pass
