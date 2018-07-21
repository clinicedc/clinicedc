from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class DosageGuidelineError(Exception):
    pass


class DosageCalculator:

    medication_model = 'edc_pharmacy.medication'

    def __init__(self, medication_name=None, dose=None, dose_units=None,
                 dose_per_kg=None, dose_frequency_factor=None, **kwargs):
        self.medication_name = medication_name
        self.dose = dose
        self.dose_per_kg = dose_per_kg
        self.dose_units = dose_units
        self.dose_frequency_factor = dose_frequency_factor
        if self.dose and self.dose_per_kg:
            raise DosageGuidelineError(
                'Specify either dose or dose_per_kg, not both.')
        try:
            self.dosage_per_kg_per_day = self.dose_per_kg * self.dose_frequency_factor
        except TypeError:
            self.dosage_per_kg_per_day = None

    @property
    def medication_model_cls(self):
        return django_apps.get_model(self.medication_model)

    def __repr(self):
        return f'{self.__class__.__name__}(medication_name=self.medication_name)'

    def dosage_per_day(self, weight_in_kgs=None, strength=None, strength_units=None):
        """Returns a decimal value or raises an exception.
        """
        if strength_units != self.dose_units:
            raise DosageGuidelineError(
                f'Invalid units. Guideline dose is in '
                f'\'{self.dose_units}\'. Got {strength_units}.')
        try:
            self.medication_model_cls.objects.get(
                name=self.medication_name,
                strength=strength,
                units=strength_units)
        except ObjectDoesNotExist:
            raise DosageGuidelineError(
                f'Invalid strength for {self.medication_name}. '
                f'Got {strength}{strength_units}')
        if self.dosage_per_kg_per_day:
            dosage_per_day = (self.dosage_per_kg_per_day
                              * weight_in_kgs) / strength
        else:
            dosage_per_day = (
                self.dose * self.dose_frequency_factor) / strength
        return dosage_per_day
