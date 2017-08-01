from django.apps import apps as django_apps


class CrfLookupError(Exception):
    pass


class Crf:

    def __init__(self, show_order=None, model=None, required=None,
                 additional=None, **kwargs):
        self.additional = additional
        self.model = model
        self.required = True if required is None else required
        self.show_order = show_order

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.show_order}, '
                f'{self.model}, {self.required})')

    def __str__(self):
        required = 'Required' if self.required else ''
        return f'{self.model} {required}'

    def validate(self):
        """Raises an exception if a CRF model lookup fails.
        """
        try:
            django_apps.get_model(*self.model.split('.'))
        except LookupError as e:
            raise CrfLookupError(e) from e
