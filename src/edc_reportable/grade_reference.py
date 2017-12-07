# from .value_reference import ValueReference
#
# G1 = '1'
# G2 = '2'
# G3 = '3'
# G4 = '4'
# G5 = '5'
#
#
# class Grade1(Exception):
#     pass
#
#
# class Grade2(Exception):
#     pass
#
#
# class Grade3(Exception):
#     pass
#
#
# class Grade4(Exception):
#     pass
#
#
# class Grade5(Exception):
#     pass
#
#
# class GradeReference(ValueReference):
#
#     def __init__(self, grade=None, gender=None, lower_age=None, upper_age=None, **kwargs):
#         super().__init__(**kwargs)
#         if grade == G1:
#             self.error_cls = Grade1
#         elif grade == G2:
#             self.error_cls = Grade2
#         elif grade == G3:
#             self.error_cls = Grade3
#         elif grade == G4:
#             self.error_cls = Grade4
#         elif grade == G5:
#             self.error_cls = Grade5
#         self.grade = grade
#         self.gender = gender
#         self.lower_age = lower_age
#         self.upper_age = upper_age
