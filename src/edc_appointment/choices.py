from .constants import IN_PROGRESS_APPT, INCOMPLETE_APPT, COMPLETE_APPT, CANCELLED_APPT, NEW_APPT

APPT_STATUS = (
    (NEW_APPT, 'New'),
    (IN_PROGRESS_APPT, 'In Progress'),
    (INCOMPLETE_APPT, 'Incomplete'),
    (COMPLETE_APPT, 'Done'),
    (CANCELLED_APPT, 'Cancelled'),
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
