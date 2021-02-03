from edc_constants.constants import MOBILE_NUMBER, NO, OTHER, YES

from .constants import HOSPITAL_NUMBER

IDENTITY_TYPE = (
    ("country_id", "Country ID number"),
    ("drivers", "Driver's license"),
    ("passport", "Passport"),
    (HOSPITAL_NUMBER, "Hospital number"),
    ("country_id_rcpt", "Country ID receipt"),
    (MOBILE_NUMBER, "Mobile number"),
    (OTHER, "Other"),
)

YES_DECLINED = "Yes_declined"

YES_NO_DECLINED_COPY = (
    (YES, "Yes and participant accepted the copy"),
    (NO, "No"),
    (YES_DECLINED, "Yes but participant declined the copy"),
)
