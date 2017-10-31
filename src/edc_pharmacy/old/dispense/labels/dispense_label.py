from edc_label.label import Label

from edc_pharma.dispense.prescription_creator import PrescriptionCreator

from .dispense_label_context import DispenseLabelContext


class DispenseLabel:
    """Print medication label given dispense timepoint record.
    """
    label_cls = Label
    label_context_cls = DispenseLabelContext
    dispense_history_creator_cls = PrescriptionCreator
    template_name = 'dispense'

    def __init__(self, dispense_appointment=None, copies=None, template_name=None,
                 prescriptions=None):
        self.copies = copies or 1
        self.dispense_appointment = dispense_appointment
        self.prescriptions = prescriptions
        self.label = self.label_cls(
            template_name=template_name or self.template_name)

        self.context_list = self.label_context_cls(
            prescriptions=self.prescriptions).context_list
        self.print_labels = self.print_labels()

    def print_labels(self):
        printed_labels = []
        for context in self.context_list or []:
            self.label.print_label(copies=self.copies, context=context)
            printed_labels.append(context)
        return printed_labels
