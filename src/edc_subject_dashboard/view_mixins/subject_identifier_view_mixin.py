from django.views.generic.base import ContextMixin


class SubjectIdentifierViewMixin(ContextMixin):

    """Adds the subject_identifier to the context.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_identifier = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.subject_identifier = self.kwargs.get('subject_identifier')
        return context
