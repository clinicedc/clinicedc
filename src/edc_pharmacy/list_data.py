from edc_constants.constants import NOT_APPLICABLE, OTHER

list_data = {
    "edc_pharmacy.formulationtype": [
        ("tablet", "Tablet"),
        ("capsule", "Capsule"),
        ("vial", "Vial"),
        ("liquid", "Liquid"),
        ("powder", "Powder"),
        ("suspension", "Suspension"),
        ("gel", "Gel"),
        ("oil", "Oil"),
        ("lotion", "Lotion"),
        ("cream", "Cream"),
        ("patch", "Patch"),
        (OTHER, "Other"),
    ],
    "edc_pharmacy.units": [
        ("mg", "mg"),
        ("ml", "ml"),
        ("g", "g"),
        (OTHER, "Other ..."),
        (NOT_APPLICABLE, "Not applicable"),
    ],
    "edc_pharmacy.route": [
        ("intramuscular", "Intramuscular"),
        ("intravenous", "Intravenous"),
        ("oral", "Oral"),
        ("topical", "Topical"),
        ("subcutaneous", "Subcutaneous"),
        ("intravaginal", "Intravaginal"),
        ("rectal", "Rectal"),
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
