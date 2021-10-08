from edc_constants.constants import NOT_APPLICABLE, OTHER

list_data = {
    "edc_pharmacy.formulation": [
        ("11", "Tablet"),
        ("12", "Capsule"),
        ("13", "Vial"),
        ("14", "Liquid"),
        ("15", "Powder"),
        ("16", "Suspension"),
        ("17", "Gel"),
        ("18", "Oil"),
        ("19", "Lotion"),
        ("20", "Cream"),
        ("21", "Patch"),
        (OTHER, "Other"),
    ],
    "edc_pharmacy.units": [
        ("mg", "mg"),
        ("ml", "ml"),
        ("g", "g"),
        (OTHER, "Other ..."),
        (NOT_APPLICABLE, "Not applicable"),
    ],
    "edc_pharmacy:route": [
        ("10", "Intramuscular"),
        ("20", "Intravenous"),
        ("30", "Oral"),
        ("40", "Topical"),
        ("50", "Subcutaneous"),
        ("60", "Intravaginal"),
        ("70", "Rectal"),
        (OTHER, "Other"),
    ],
    "edc_pharmacy.frequencyunits": [
        ("hr", "times per hour"),
        ("day", "times per day"),
        ("single", "single dose"),
        (OTHER, "Other ..."),
        (NOT_APPLICABLE, "Not applicable"),
    ],
}
