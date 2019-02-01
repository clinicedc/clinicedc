from .model_notification import ModelNotification


class NewModelNotification(ModelNotification):
    def notify_on_condition(self, instance=None, **kwargs):
        return (
            instance._meta.label_lower == self.model
            and instance.history.all().count() == 1
        )
