import sys

from django.conf import settings

from .action_item import (
    ActionItem,
    ActionItemUpdatesRequireFollowup,
    SubjectDoesNotExist,
)
from .action_model_mixin import ActionModelMixin, ActionNoManagersModelMixin
from .action_type import ActionType, ActionTypeError
from .reference import Reference
from .signals import (
    action_item_notification_on_post_create_historical_record,
    action_on_reference_model_post_delete,
    update_action_item_reason_on_m2m_changed,
    update_or_create_action_item_on_m2m_change,
    update_or_create_action_item_on_post_save,
)

if (
    settings.APP_NAME == "edc_action_item"
    and "migrate" not in sys.argv
    and "makemigrations" not in sys.argv
):
    from ..tests import models
