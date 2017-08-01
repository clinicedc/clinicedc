from django.core.exceptions import ImproperlyConfigured


class SubjectType:

    def __init__(self, name, verbose_name, *caps):
        self.name = name
        self.caps = {}
        for cap in caps:
            if cap.subject_type_name and cap.subject_type_name != self.name:
                raise ImproperlyConfigured(
                    f'Cannot add enrollment cap for {cap.subject_type_name} '
                    f'to subject type {self.name}.')
            if not cap.subject_type_name:
                cap.subject_type_name = self.name
            self.caps.update({cap.subject_type_name: cap})

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __str__(self):
        return '\'{}\' enrolled using \'{}\''.format(
            self.name, ', '.join(['{} (Cap={})'.format(
                cap.model_name, cap.max_subjects) for cap in self.caps.values()]))
