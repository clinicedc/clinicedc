from .model_notification import ModelNotification


class UpdatedModelNotification(ModelNotification):

    fields = ['modified']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.changed_fields = {}

    def callback(self, instance=None, **kwargs):
        if self.fields and instance.history.all().count() > 1:
            if instance._meta.label_lower == self.model:
                changes = {}
                for field in self.fields:
                    values = [
                        getattr(obj, field)
                        for obj in instance.history.all().order_by('history_date')]
                    values.reverse()
                    changes.update({field: values[:2]})
                for field, values in changes.items():
                    try:
                        changed = values[0] != values[1]
                    except IndexError:
                        pass
                    else:
                        if changed:
                            self.changed_fields.update({field: values})
        return self.changed_fields
