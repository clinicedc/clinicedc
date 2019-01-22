import sys

from django.conf import settings

from .action_item import (
    ActionItem,
    ActionItemUpdatesRequireFollowup,
    SubjectDoesNotExist,
)
from .action_model_mixin import ActionModelMixin
from .action_type import ActionType, ActionTypeError
from .reference import Reference

if (
    settings.APP_NAME == "edc_action_item"
    and "migrate" not in sys.argv
    and "makemigrations" not in sys.argv
):
    from ..tests import models
