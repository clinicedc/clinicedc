from edc_constants.constants import NOT_APPLICABLE, OTHER, NEW

from .constants import PARTIAL, FILLED, CANCELLED, DISPENSED


PRESCRIPTION_STATUS = (
    (NEW, 'New'),
    (PARTIAL, 'Partially filled'),
    (FILLED, 'Filled'),
    (CANCELLED, 'Cancelled'),
)


DISPENSE_STATUS = (
    (NEW, 'New'),
    (DISPENSED, 'Dispensed'),
    (CANCELLED, 'Cancelled'),
)


DRUG_FORMULATION = (
    ('11', 'Tablet'),
    ('12', 'Capsule'),
    ('13', 'Vial'),
    ('14', 'Liquid'),
    ('15', 'Powder'),
    ('16', 'Suspension'),
    ('17', 'Gel'),
    ('18', 'Oil'),
    ('19', 'Lotion'),
    ('20', 'Cream'),
    ('21', 'Patch'),
    (OTHER, 'Other'),
)

DRUG_ROUTE = (
    ('10', 'Intramuscular'),
    ('20', 'Intravenous'),
    ('30', 'Oral'),
    ('40', 'Topical'),
    ('50', 'Subcutaneous'),
    ('60', 'Intravaginal'),
    ('70', 'Rectal'),
    (OTHER, 'Other'),
)

UNITS = (
    ('mg', 'mg'),
    ('ml', 'ml'),
    ('g', 'g'),
    (OTHER, 'Other ...'),
    (NOT_APPLICABLE, 'Not applicable'),
)

TIMING = (
    ('hr', 'times per hour'),
    ('day', 'times per day'),
    ('single', 'single dose'),
    (OTHER, 'Other ...'),
    (NOT_APPLICABLE, 'Not applicable'),
)

FREQUENCY = (
    ('hr', 'per hour'),
    ('day', 'per day'),
    ('single', 'single dose'),
    (OTHER, 'Other ...'),
    (NOT_APPLICABLE, 'Not applicable'),
)
