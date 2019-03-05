from django.apps import apps as django_apps


class PrescriptionApprovalValidatorError(Exception):
    pass


class PrescriptionApprovalValidator:
    app_config = django_apps.get_app_config("edc_pharma")

    def __init__(self, prescriptions=None):

        for prescription in prescriptions:
            appointment = prescription.dispense_appointment
            previous = appointment.previous()
            if previous:
                Prescription = self.app_config.get_model("prescription")
                prescriptions = Prescription.objects.filter(
                    is_approved=False, dispense_appointment=previous
                )
                if prescriptions:
                    raise PrescriptionApprovalValidatorError(
                        f"Future prescriptions cannot be approved. Approve "
                        f"prescriptions for dispensing date {previous.appt_datetime}"
                    )
