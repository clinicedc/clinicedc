import sys

from django.conf import settings

from .reference import Reference
from .action_item import ActionItem, ActionItemUpdatesRequireFollowup, SubjectDoesNotExist
from .action_item_update import ActionItemUpdate
from .action_type import ActionType, ActionTypeError
from .action_model_mixin import ActionModelMixin

if (settings.APP_NAME == 'edc_action_item'
        and 'migrate' not in sys.argv
        and 'makemigrations' not in sys.argv):
    from ..tests import models
