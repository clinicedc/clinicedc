from .model_notification import ModelNotification


class UpdatedModelNotification(ModelNotification):

    fields = ["modified"]

    email_subject_template = (
        "*UPDATE* {test_subject_line}{protocol_name}: "
        "{display_name} "
        "for {instance.subject_identifier}"
    )

    def notify_on_condition(self, instance=None, **kwargs):
        changed_fields = {}
        if self.fields and instance.history.all().count() > 1:
            changes = {}
            for field in self.fields:
                values = [
                    getattr(obj, field)
                    for obj in instance.history.all().order_by("history_date")
                ]
                values.reverse()
                changes.update({field: values[:2]})
            for field, values in changes.items():
                changed = values[0] != values[1]
                if changed:
                    changed_fields.update({field: values})
        return changed_fields
