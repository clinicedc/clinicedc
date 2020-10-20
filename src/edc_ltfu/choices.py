from edc_constants.constants import OTHER

LOSS_CHOICES = (
    ("unknown_address", "Changed to an unknown address"),
    ("never_returned", "Did not return despite reminders"),
    ("bad_contact_details", "Inaccurate contact details"),
    (OTHER, "Other"),
)
