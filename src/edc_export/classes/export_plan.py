

class ExportPlan(object):

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.app_label = kwargs.get('app_label')
        self.object_name = kwargs.get('object_name')
        self.fields = kwargs.get('field')
        self.extra_fields = kwargs.get('extra_fields')
        self.exclude = kwargs.get('exclude')
        self.header = kwargs.get('header')
        self.track_history = kwargs.get('track_history')
        self.show_all_fields = kwargs.get('show_all_fields')
        self.delimiter = kwargs.get('delimiter')
        self.encrypt = kwargs.get('encrypt')
        self.strip = kwargs.get('strip')
        self.target_path = kwargs.get('target_path')
        self.notification_plan_name = kwargs.get('notification_plan')

    def __repr__(self):
        return '{0}({1.name!r})'.format(self.__class__.__name__, self)

    def __str__(self):
        return '{0.name!r}'.format(self)
