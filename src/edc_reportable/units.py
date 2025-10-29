from django.utils.safestring import mark_safe

CELLS_PER_MILLIMETER_CUBED_DISPLAY = mark_safe("cells/mm<sup>3</sup>")  # nosec B308
IU_LITER_DISPLAY = mark_safe("IU/L")  # nosec B308
MICROMOLES_PER_LITER_DISPLAY = "μmol/L (micromoles/L)"
MICRO_IU_MILLILITER_DISPLAY = mark_safe("μIU/mL")  # nosec B308
MILLIMOLES_PER_LITER_DISPLAY = "mmol/L (millimoles/L)"
MILLI_IU_LITER_DISPLAY = mark_safe("mIU/L")  # nosec B308
MM3_DISPLAY = mark_safe("mm<sup>3</sup>")  # nosec B308
TEN_X_3_PER_LITER_DISPLAY = mark_safe("10<sup>3</sup>/L")  # nosec B308
TEN_X_9_PER_LITER_DISPLAY = mark_safe("10<sup>9</sup>/L")  # nosec B308
