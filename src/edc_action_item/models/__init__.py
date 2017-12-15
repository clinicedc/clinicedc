import sys

from django.conf import settings

from .action_item import ActionItem, ActionItemUpdatesRequireFollowup, SubjectDoesNotExist
from .action_item_update import ActionItemUpdate
from .action_type import ActionType, ActionTypeError

if (settings.APP_NAME == 'edc_action_item'
        and 'migrate' not in sys.argv
        and 'makemigrations' not in sys.argv):
    from ..tests import models
