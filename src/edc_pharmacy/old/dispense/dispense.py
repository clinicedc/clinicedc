from edc_pharma.models import WorkList

from django.apps import apps as django_apps

from ..constants import PRINT_SELECTED
from ..dispense.labels import DispenseLabel
from ..models import DispenseAppointment, Prescription


edc_pharma_app_config = django_apps.get_app_config("edc_pharma")


class Dispense:

    """Print dispense labels and update dispense history.
    """

    print_label_cls = DispenseLabel

    def __init__(
        self,
        subject_identifier=None,
        appointment_id=None,
        user=None,
        prescriptions=None,
        action=None,
    ):
        self.subject_identifier = subject_identifier
        self.appointment_id = appointment_id
        self._prescriptions = prescriptions
        self.user = user
        self.action = action
        self.printed_labels = self.print_labels()

    @property
    def prescriptions(self):
        if self.action == PRINT_SELECTED:
            return self._prescriptions
        else:
            return Prescription.objects.filter(
                dispense_appointment__id=self.appointment_id
            )

    @property
    def dispense_appointment(self):
        """Returns dispense timepoint."""
        return DispenseAppointment.objects.get(
            schedule__subject_identifier=self.subject_identifier, id=self.appointment_id
        )

    def print_labels(self):
        """Print labels using dispense profile. """
        printer = self.print_label_cls(
            prescriptions=self.prescriptions,
            copies=1,
            template_name=edc_pharma_app_config.template_name,
        )
        return printer.print_labels


class MedicationNotApprovedError(Exception):
    pass


class DispenseAction:
    def __init__(self, appointment_id=None):
        self.appointment_id = appointment_id
        dispense_appt = DispenseAppointment.objects.get(id=self.appointment_id)
        self.validate(appointment=dispense_appt)
        dispense_appt.is_dispensed = True
        dispense_appt.save()
        self.update_worklist(appointment=dispense_appt)

    def validate(self, appointment=None):
        if Prescription.objects.filter(
            is_approved=False, dispense_apppointment=appointment
        ):
            raise MedicationNotApprovedError(
                f"Prescirption not approved error! "
                "Please approve prescriptions you want to dispense. "
            )

    def next_appointment(self, appointment=None):

        next_appointment = appointment.next()
        if next_appointment:
            return next_appointment
        pending_appointment = DispenseAppointment.objects.filter(
            is_dispensed=False, subject_identifier=appointment.subject_identifier
        ).order_by("appt_datetime")
        if pending_appointment:
            return pending_appointment.first()

    def update_worklist(self, appointment=None):
        appt = self.next_appointment(appointment=appointment)
        worklist = WorkList.objects.get(
            subject_identifier=appointment.subject_identifier
        )
        worklist.next_dispensing_datetime = appt.dispense_datetime
        worklist.save()
