from django.apps import apps as django_apps


class Crf:

    def __init__(self, show_order=None, model=None, required=None,
                 additional=None, **kwargs):
        self.additional = additional
        self.model_label_lower = model
        self.required = True if required is None else required
        self.show_order = show_order

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.show_order}, '
                f'{self.model_label_lower}, {self.required})')

    def __str__(self):
        required = 'Required' if self.required else ''
        return f'{self.model_label_lower} {required}'

    @property
    def model(self):
        return django_apps.get_model(*self.model_label_lower.split('.'))
