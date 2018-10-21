from django.apps import apps as django_apps
from django.conf import settings
from edc_notification.notification import Notification


class NewModelNotification(Notification):

    model = None
    email_to = [f'notifications.{settings.APP_NAME}@example.com']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.display_name:
            self.display_name = django_apps.get_model(
                self.model)._meta.verbose_name.title()

    def callback(self, instance=None, **kwargs):
        if instance._meta.label_lower == self.model:
            return instance.history.all().count() == 1
        return False
