from edc_pharma.constants import CAPSULE

from .capsule_dosage import CapsuleDosage
from .vial_dosage import VialDosage


class MedicationDosage:
    """Given a medication definition and subject weight the class calculates the 
    quantity of medication or the volume to dispense.
    For Example.
        Amphotericin B
        weight = 32kg, unit=1mg, category=vial, amount=50, duration = 7 days
        Number of Dispenses/vial size in mg = (weight * unit * duration) / amount

    """

    capsule_dosage_cls = CapsuleDosage
    vial_dosage_cls = VialDosage

    def __init__(self, medication_definition=None, weight=None, duration=None):
        self.definition = medication_definition
        self.weight = weight
        if self.definition.single_dose:
            self.duration = 1
        else:
            self.duration = duration

    @property
    def capsules(self):
        return self.capsule_dosage_cls(
            body_weight=self.weight,
            strength=self.definition.strength,
            millgrams_per_vial=self.definition.milligram,
            duration=self.duration,
            use_body_weight=self.definition.use_body_weight)

    @property
    def required_quantity(self):
        result = None
        if self.definition == CAPSULE:
            result = self.capsules
        else:
            result = self.vials
        return result.required_quantity

    @property
    def vials(self):
        result = self.vial_dosage_cls(
            body_weight=self.weight, strength_of_vial=self.definition.strength,
            millgrams_per_vial=self.definition.milligram,
            duration=self.duration,
            use_body_weight=self.definition.use_body_weight)
        return result

    def __repr__(self):
        return f'{self.definition.description}'
