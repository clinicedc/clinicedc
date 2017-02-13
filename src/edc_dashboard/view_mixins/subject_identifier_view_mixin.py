

class SubjectIdentifierViewMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_identifier = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('SubjectIdentifierViewMixin')
        self.subject_identifier = self.kwargs.get('subject_identifier')
        return context
