from edc_constants.constants import NEW, OPEN, CLOSED

from .constants import RESOLVED, REJECTED, FEEDBACK

ACTION_STATUS = (
    (NEW, 'New'),
    (OPEN, 'Open'),
    (RESOLVED, 'Resolved'),
    (CLOSED, 'Closed'),
    (FEEDBACK, 'Feedback'),
    (REJECTED, 'Rejected'),
)
