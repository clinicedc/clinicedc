from edc_constants.constants import NOT_APPLICABLE, OTHER

from .constants import DIET_LIFESTYLE, DRUGS, INSULIN, THIS_CLINIC

CARE_ACCESS = (
    (THIS_CLINIC, "Patient comes to this facility for their care"),
    (OTHER, "Patient goes to a different clinic"),
    (NOT_APPLICABLE, "Not applicable"),
)

CHOL_MANAGEMENT = (
    (DRUGS, "Oral drugs"),
    (DIET_LIFESTYLE, "Diet and lifestyle alone"),
)
DM_MANAGEMENT = (
    (INSULIN, "Insulin injections"),
    (DRUGS, "Oral drugs"),
    (DIET_LIFESTYLE, "Diet and lifestyle alone"),
)

HTN_MANAGEMENT = (
    (DRUGS, "Drugs / Medicine"),
    (DIET_LIFESTYLE, "Diet and lifestyle alone"),
)
