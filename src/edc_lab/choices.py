from edc_constants.constants import PENDING, PARTIAL, COMPLETE

ABS_CALC = (
    ('absolute', 'Absolute'),
    ('calculated', 'Calculated'),
)

ALIQUOT_STATUS = (
    ('available', 'available'),
    ('consumed', 'consumed'),
)

MODIFY_ACTIONS = (
    ('INSERT', 'Insert'),
    ('UPDATE', 'Update'),
    ('DELETE', 'Delete'),
    ('PRINT', 'Print'),
    ('VIEW', 'Print'),
)

ORDER_STATUS = (
    (PENDING, 'Pending'),
    (PARTIAL, 'Partial'),
    (COMPLETE, 'Complete'),
)

RESULT_RELEASE_STATUS = (
    ('NEW', 'New'),
    ('RELEASED', 'Released'),
    ('AMENDED', 'Amended'),
)

RESULT_VALIDATION_STATUS = (
    ('P', 'Preliminary'),
    ('F', 'Final'),
    ('R', 'Rejected'),
)

RESULT_QUANTIFIER = (
    ('=', '='),
    ('>', '>'),
    ('>=', '>='),
    ('<', '<'),
    ('<=', '<='),
)

SPECIMEN_MEASURE_UNITS = (
    ('mL', 'mL'),
    ('uL', 'uL'),
    ('spots', 'spots'),
    ('n/a', 'Not Applicable'),
)

SPECIMEN_MEDIUM = (
    ('tube_any', 'Tube'),
    ('tube_edta', 'Tube EDTA'),
    ('swab', 'Swab'),
    ('dbs_card', 'DBS Card'),
)

UNITS = (
    ('%', '%'),
    ('10^3/uL', '10^3/uL'),
    ('10^3uL', '10^3uL'),
    ('10^6/uL', '10^6/uL'),
    ('cells/ul', 'cells/ul'),
    ('copies/ml', 'copies/ml'),
    ('fL', 'fL'),
    ('g/dL', 'g/dL'),
    ('g/L', 'g/L'),
    ('mg/L', 'mg/L'),
    ('mm/H', 'mm/H'),
    ('mmol/L', 'mmol/L'),
    ('ng/ml', 'ng/ml'),
    ('pg', 'pg'),
    ('ratio', 'ratio'),
    ('U/L', 'U/L'),
    ('umol/L', 'umol/L'),
)
