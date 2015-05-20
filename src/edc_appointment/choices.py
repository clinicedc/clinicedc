from .constants import IN_PROGRESS, INCOMPLETE, DONE, CANCELLED, OTHER

APPT_STATUS = (
    ('new', 'New'),
    (IN_PROGRESS, 'In Progress'),
    (INCOMPLETE, 'Incomplete'),
    (DONE, 'Done'),
    (CANCELLED, 'Cancelled')
)

APPT_TYPE = (
    ('clinic', 'In clinic'),
    ('telephone', 'By telephone'),
    ('home', 'At home'),
)

INFO_PROVIDER = (
    ('subject', 'Subject'),
    (OTHER, 'Other person'),
)
