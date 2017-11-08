from django.views.generic.base import ContextMixin


class ShowHideViewMixin(ContextMixin):

    """Adds show_forms to the context.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_forms = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.show_forms = self.kwargs.get('show_forms')
        context.update(show_forms=self.show_forms)
        return context
