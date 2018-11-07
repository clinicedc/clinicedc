from .model_notification import ModelNotification


class NewModelNotification(ModelNotification):

    def notify_on_condition(self, instance=None, **kwargs):
        if instance._meta.label_lower == self.model:
            return instance.history.all().count() == 1
        return False
