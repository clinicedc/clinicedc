from edc_constants.constants import OTHER, NEW, IN_PROGRESS, INCOMPLETE, COMPLETE, CANCELLED

from .constants import CLINIC_APPT, TELEPHONIC_APPT, HOME_APPT

__all__ = ['APPT_STATUS', 'APPT_TYPE', 'INFO_PROVIDER']

APPT_STATUS = (
    (NEW, 'New'),
    (IN_PROGRESS, 'In Progress'),
    (INCOMPLETE, 'Incomplete'),
    (COMPLETE, 'Complete'),
    (CANCELLED, 'Cancelled')
)

APPT_TYPE = (
    (CLINIC_APPT, 'In clinic'),
    (TELEPHONIC_APPT, 'By telephone'),
    (HOME_APPT, 'At home'),
)

INFO_PROVIDER = (
    ('subject', 'Subject'),
    (OTHER, 'Other person'),
)
