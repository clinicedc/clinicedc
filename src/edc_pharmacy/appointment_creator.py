from edc_appointment.creators import AppointmentCreator \
    as BaseAppointmentCreator


class AppointmentCreator(BaseAppointmentCreator):

    """Creates dispense timepoints and update.
    """

    appointment_model = 'edc_pharmacy.appointment'
    # profile_selector_cls = DispenseProfileSelector

#     def __init__(self, schedule_name=None, schedule_plan=None,
#                  subject_identifier=None, schedule=None, timepoints=None):
#         self.schedule = schedule
#         self.schedule_name = schedule_name
#         self.schedule_plan = schedule_plan
#         self.subject_identifier = subject_identifier
#         self.timepoints = timepoints

#     def create(self):
#         profile_selector = self.profile_selector_cls(
#             subject_identifier=self.subject_identifier,
#             schedule_name=self.schedule_name,
#             schedule_plan=self.schedule_plan)
#         appointments = []
#         for code in self.timepoints:
#             timepoint = self.timepoints.get(code)
#             try:
#                 appointment = DispenseAppointment.objects.get(
#                     schedule=self.schedule,
#                     appt_datetime=timepoint.timepoint_datetime,
#                     profile_label=profile_selector.profile.label)
#             except DispenseAppointment.DoesNotExist:
#                 appointment = DispenseAppointment.objects.create(
#                     schedule=self.schedule,
#                     profile_label=profile_selector.profile.label,
#                     appt_datetime=timepoint.timepoint_datetime)
#             appointments.append(appointment)
#         return appointments
