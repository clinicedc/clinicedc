from django.conf import settings
from edc_notification.notification import Notification


class NewModelNotification(Notification):

    model = None
    email_to = [f'notifications.{settings.APP_NAME}@example.com']

    def callback(self):
        if self.instance._meta.label_lower == self.model:
            return self.created
        return False
