from ..constants import UPDATE
from .model_notification import ModelNotification


class UpdatedModelNotification(ModelNotification):

    model_operations = [UPDATE]

    update_fields = ["modified"]

    email_subject_template = (
        "*UPDATE* {test_subject_line}{protocol_name}: "
        "{display_name} "
        "for {instance.subject_identifier}"
    )
