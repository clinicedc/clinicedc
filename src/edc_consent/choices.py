from edc_constants.constants import YES, NO, OTHER

IDENTITY_TYPE = (
    ("country_id", "Country ID number"),
    ("drivers", "Driver's license"),
    ("passport", "Passport"),
    ("hospital_no", "Hospital number"),
    ("country_id_rcpt", "Country ID receipt"),
    (OTHER, "Other"),
)

YES_DECLINED = "Yes_declined"

YES_NO_DECLINED_COPY = (
    (YES, "Yes and participant accepted the copy"),
    (NO, "No"),
    (YES_DECLINED, "Yes but participant declined the copy"),
)
