from django.apps import apps as django_apps


class PrescriptionApprovalValidatorError(Exception):
    pass


class ApprovePrescription:

    prescription_model = 'edc_pharmacy.prescription'

    def __init__(self, prescription_model_obj=None):
        dispense_appointment = prescription_model_obj.dispense_appointment
        previous_appointment = dispense_appointment.previous()
        if previous_appointment:
            if model_cls.objects.filter(
                    is_approved=False, dispense_appointment=previous_appointment).exists():
                raise PrescriptionApprovalValidatorError(
                    f"Future prescriptions cannot be approved. Approve "
                    f"prescriptions for dispensing date {previous_appointment.appt_datetime}")
