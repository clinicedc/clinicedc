from django.apps import apps as django_apps

from .notification import Notification


class ModelNotification(Notification):

    model = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.display_name:
            self.display_name = django_apps.get_model(
                self.model)._meta.verbose_name.title()

    def post_notification_action(self, instance=None, **kwargs):
        pass
