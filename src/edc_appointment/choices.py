from edc_constants.constants import IN_PROGRESS, INCOMPLETE, COMPLETE_APPT, CANCELLED, NEW_APPT

APPT_STATUS = (
    (NEW_APPT, 'New'),
    (IN_PROGRESS, 'In Progress'),
    (INCOMPLETE, 'Incomplete'),
    (COMPLETE_APPT, 'Done'),
    (CANCELLED, 'Cancelled'),
)

APPT_TYPE = (
    ('clinic', 'In clinic'),
    ('telephone', 'By telephone'),
    ('home', 'At home'),
)

INFO_PROVIDER = (
    ('subject', 'Subject'),
    ('other', 'Other person'),
)
