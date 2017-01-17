

class SubjectIdentifierViewMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_identifier = None

    def get(self, request, *args, **kwargs):
        self.subject_identifier = kwargs.get('subject_identifier')
        return super().get(request, *args, **kwargs)
