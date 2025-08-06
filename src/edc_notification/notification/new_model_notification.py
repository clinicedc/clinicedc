from ..constants import CREATE
from .model_notification import ModelNotification


class NewModelNotification(ModelNotification):
    model_operations = [CREATE]
