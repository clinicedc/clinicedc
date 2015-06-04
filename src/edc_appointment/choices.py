from edc_constants.constants import OTHER

from .constants import IN_PROGRESS, INCOMPLETE, COMPLETE, CANCELLED

APPT_STATUS = (
    ('new', 'New'),
    (IN_PROGRESS, 'In Progress'),
    (INCOMPLETE, 'Incomplete'),
    (COMPLETE, 'Complete'),
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
