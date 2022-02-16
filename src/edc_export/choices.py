from .constants import CSV, STATA_10, STATA_13, STATA_14, STATA_15

EXPORT_FORMATS = (
    (CSV, "CSV (delimited by pipe `|`)"),
    (STATA_10, "Stata v10 or later"),
    (STATA_13, "Stata v13 or later"),
    (STATA_14, "Stata v14 or later"),
    (STATA_15, "Stata v15 or later"),
)
