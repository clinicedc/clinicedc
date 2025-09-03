# from __future__ import annotations
#
# from datetime import datetime
# from decimal import Decimal
# from typing import Any, Type
#
# from edc_appointment.constants import IN_PROGRESS_APPT
# from edc_appointment.models import Appointment
# from edc_appointment.utils import get_appointment_model_cls
# from edc_visit_tracking.constants import UNSCHEDULED
# from edc_visit_tracking.models import SubjectVisit
#
#
# class AppointmentTestCaseMixin:
#
#     def get_timepoint_from_visit_code(
#         self: Any,
#         instance: Any,
#         visit_code: str,
#     ) -> float | Decimal | None:
#         timepoint = None
#         for v in instance.schedule.visits.timepoints:
#             if v.name == visit_code:
#                 timepoint = v.timepoint
#                 break
#         return timepoint
#
#     def get_appointment(
#         self,
#         subject_identifier: str | None = None,
#         visit_code: str | None = None,
#         visit_code_sequence: int | None = None,
#         reason: str | None = None,
#         appt_datetime: datetime | None = None,
#         timepoint: float | Decimal | None = None,
#     ) -> Appointment:
#         if timepoint is not None:
#             appointment = get_appointment_model_cls().objects.get(
#                 subject_identifier=subject_identifier,
#                 timepoint=timepoint,
#                 visit_code_sequence=visit_code_sequence,
#             )
#         else:
#             appointment = get_appointment_model_cls().objects.get(
#                 subject_identifier=subject_identifier,
#                 visit_code=visit_code,
#                 visit_code_sequence=visit_code_sequence,
#             )
#         if appt_datetime:
#             appointment.appt_datetime = appt_datetime
#             appointment.save()
#             appointment.refresh_from_db()
#         if reason == UNSCHEDULED:
#             appointment = self.create_unscheduled_appointment(appointment)
#         appointment.appt_status = IN_PROGRESS_APPT
#         appointment.save()
#         appointment.refresh_from_db()
#         return appointment
#
#     @staticmethod
#     def get_visit_codes(
#         model_cls: Type[Appointment | SubjectVisit], order_by: str = None
#     ):
#         return [
#             f"{o.visit_code}.{o.visit_code_sequence}"
#             for o in model_cls.objects.all().order_by(order_by)
#         ]
#
#
# # class AppointmentAppTestCaseMixin:
# #     helper_cls = None
# #
# #     def setUp(self):
# #         super().setUp()
# #         site_visit_schedules._registry = {}
# #         self.visit_schedule1 = get_visit_schedule1()
# #         self.visit_schedule2 = get_visit_schedule2()
# #         self.visit_schedule3 = get_visit_schedule3()
# #         site_visit_schedules.register(self.visit_schedule1)
# #         site_visit_schedules.register(self.visit_schedule2)
# #         site_visit_schedules.register(self.visit_schedule3)
# #         site_consents.registry = {}
# #         site_consents.register(consent_v1)
# #         helper = self.helper_cls(
# #             now=ResearchProtocolConfig().study_open_datetime,
# #         )
# #         subject_consent = helper.consent_and_put_on_schedule(
# #             visit_schedule_name=self.visit_schedule1.name,
# #             schedule_name="schedule1",
# #             consent_definition=consent_v1,
# #         )
# #         self.subject_identifier = subject_consent.subject_identifier
# #         appointments = Appointment.objects.filter(
# #             subject_identifier=self.subject_identifier
# #         )
# #         self.assertEqual(appointments.count(), 4)
# #
# #         appointment = Appointment.objects.get(timepoint=0.0)
# #         self.create_related_visit(appointment)
# #         self.create_unscheduled_appointments(appointment)
# #
# #         self.appt_datetimes = [
# #             o.appt_datetime for o in Appointment.objects.all().order_by("appt_datetime")
# #         ]
# #
# #     def create_unscheduled_appointments(self, appointment):
# #         for i in range(0, 3):
# #             creator = UnscheduledAppointmentCreator(
# #                 subject_identifier=self.subject_identifier,
# #                 visit_schedule_name=self.visit_schedule1.name,
# #                 schedule_name="schedule1",
# #                 visit_code="1000",
# #                 suggested_visit_code_sequence=appointment.visit_code_sequence + 1,
# #             )
# #             appointment = creator.appointment
# #             appointment.appt_status = INCOMPLETE_APPT
# #             appointment.save_base(update_fields=["appt_status"])
# #
# #     @staticmethod
# #     def create_related_visit(
# #         appointment: Appointment, reason: str | None = None
# #     ) -> SubjectVisit:
# #         if not appointment.related_visit:
# #             related_visit = SubjectVisit.objects.create(
# #                 appointment=appointment,
# #                 subject_identifier=appointment.subject_identifier,
# #                 report_datetime=appointment.appt_datetime,
# #                 visit_schedule_name=appointment.visit_schedule_name,
# #                 schedule_name=appointment.schedule_name,
# #                 visit_code=appointment.visit_code,
# #                 visit_code_sequence=appointment.visit_code_sequence,
# #                 reason=reason or SCHEDULED,
# #             )
# #             appointment.appt_status = INCOMPLETE_APPT
# #             appointment.save_base(update_fields=["appt_status"])
# #             appointment.refresh_from_db()
# #         else:
# #             related_visit = appointment.related_visit
# #         return related_visit
# #
# #     @staticmethod
# #     def get_visit_codes(
# #         model_cls: Type[Appointment | SubjectVisit], order_by: str = None
# #     ):
# #         return [
# #             f"{o.visit_code}.{o.visit_code_sequence}"
# #             for o in model_cls.objects.all().order_by(order_by)
# #         ]
