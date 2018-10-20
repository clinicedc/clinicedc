from django.conf import settings
from edc_notification.notification import Notification


class UpdatedModelNotification(Notification):

    model = None
    fields = ['modified']
    email_to = [f'notifications.{settings.APP_NAME}@example.com']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.changed_fields = {}

    def callback(self):
        if not self.created and self.fields:
            if self.instance._meta.label_lower == self.model:
                changes = {}
                for field in self.fields:
                    values = [
                        getattr(obj, field)
                        for obj in self.instance.history.all().order_by('history_date')]
                    values.append(getattr(self.instance, field))
                    changes.update({field: values[-2:]})
                for field, values in changes.items():
                    try:
                        changed = values[0] != values[1]
                    except IndexError:
                        pass
                    else:
                        if changed:
                            self.changed_fields.update({field: values})
        return self.changed_fields
