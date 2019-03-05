from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from ..medications import medications
from ..models import Prescription, MedicationDefinition


class PrescriptionCreator:
    """Creates all prescription records after completing patient history model.
    """

    def __init__(
        self, appointment=None, selected=None, medication_name=None, options=None
    ):
        self.medication_name = medication_name
        self.appointment = appointment
        self.selected = selected
        self.options = options
        self.save_or_update()

    def create_all(self):
        """Create prescription record per medication and update the next
        refill datetime.
        """
        if self.selected:
            medication_definition = medications.get(self.medication_name)
            self.create_history(medication_definition=medication_definition)
        else:
            for medication_definition in self.appointment.profile_medications:
                self.create_prescription(medication_definition=medication_definition)
        self.appointment.update_next_dispense_datetime()

    def medication(self, medication_definition=None):
        try:
            medication_obj = MedicationDefinition.objects.get(
                name=medication_definition.name
            )
        except ObjectDoesNotExist:
            medication_obj = MedicationDefinition.objects.create(
                name=medication_definition.name,
                unit=medication_definition.unit,
                category=medication_definition.category,
                description=medication_definition.description,
                single_dose=medication_definition.single_dose,
                use_body_weight=medication_definition.use_body_weight,
                milligram=medication_definition.milligram,
                strength=medication_definition.strength,
            )
        return medication_obj

    def create_prescription(self, medication_definition=None):

        medication_obj = self.medication(medication_definition=medication_definition)
        model_obj = self.prescription(medication_definition=medication_obj)
        model_obj.save()

    def save_or_update(self):
        self.create_all()
        self.appointment.save()

    def prescription(self, medication_definition=None):
        try:
            prescription = Prescription.objects.get(
                appointment=self.appointment,
                medication_definition=medication_definition,
            )
        except Prescription.DoesNotExist:
            prescription = Prescription.objects.create(
                appointment=self.appointment,
                dispense_datetime=datetime.today(),
                medication_definition=medication_definition,
                subject_identifier=self.appointment.subject_identifier,
                medication_description=medication_definition.description,
                category=medication_definition.category,
                **self.options
            )
        return prescription
