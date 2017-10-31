from edc_pharma.constants import MILLIGRAM, CAPSULE, VIAL


class MedicationDefinition:
    def __init__(self, name=None, description=None, category=None,
                 unit=None, milligram=None, strength=None,
                 number_of_times_per_day=None, use_body_weight=None,
                 single_dose=None):
        self.name = name
        self.description = description
        self.category = category
        self.unit = unit
        self.milligram = milligram
        self.strength = strength
        self.number_of_times_per_day = number_of_times_per_day
        self.use_body_weight = use_body_weight
        self.single_dose = single_dose


medications = {}
ambisome = MedicationDefinition(
    name='ambisome',
    description='Ambisome 10 mg/kg/day',
    category=VIAL,
    unit=MILLIGRAM,
    milligram=10,
    strength=50,
    number_of_times_per_day=4,
    use_body_weight=True,
    single_dose=True)

medications.update({'ambisome': ambisome})

fluconazole_800 = MedicationDefinition(
    name='fluconazole_800mg',
    description='Fluconazole 800mg/day',
    category=VIAL,
    unit=MILLIGRAM,
    milligram=800,
    strength=500,
    number_of_times_per_day=4,
    use_body_weight=False,
    single_dose=False)
medications.update({'fluconazole_800mg': fluconazole_800})

fluconazole_1200 = MedicationDefinition(
    name='fluconazole_1200mg',
    description='Fluconazole 1200mg/day',
    category=VIAL,
    unit=MILLIGRAM,
    milligram=1200,
    strength=500,
    number_of_times_per_day=4,
    use_body_weight=False,
    single_dose=False)
medications.update({'fluconazole_1200mg': fluconazole_1200})

flucytosine = MedicationDefinition(
    name='flucytosine',
    description='Flucytosine 100mg/kg/day',
    category=CAPSULE,
    unit=MILLIGRAM,
    milligram=100,
    strength=500,
    number_of_times_per_day=4,
    use_body_weight=True,
    single_dose=False)
medications.update({'flucytosine': flucytosine})

amphotericin = MedicationDefinition(
    name='amphotericin',
    description='Amphotericin B deoxycholate 1mg/kg/day',
    category=VIAL,
    unit=MILLIGRAM,
    milligram=1,
    strength=50,
    number_of_times_per_day=4,
    use_body_weight=True,
    single_dose=True)
medications.update({'amphotericin': amphotericin})

liposomal_amphotericin = MedicationDefinition(
    name='liposomal_amphotericin',
    description='Liposomal Amphotericin B 10mg/kg/day',
    category=VIAL,
    unit=MILLIGRAM,
    milligram=1,
    strength=50,
    number_of_times_per_day=4,
    use_body_weight=True,
    single_dose=True)
medications.update({'liposomal_amphotericin': liposomal_amphotericin})
