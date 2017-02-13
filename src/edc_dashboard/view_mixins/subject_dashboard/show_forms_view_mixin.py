
class ShowHideViewMixin:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_forms = None

    def get_context_data(self, **kwargs):
        """Overidden to add show_forms to the view instance.
        """
        context = super().get_context_data(**kwargs)
        print('ShowHideViewMixin')
        self.show_forms = self.kwargs.get('show_forms')
        context.update(show_forms=self.show_forms)
        return context
