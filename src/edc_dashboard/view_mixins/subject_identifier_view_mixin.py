

class SubjectIdentifierViewMixin:

    dashboard_url = 'dashboard_url'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_identifier = None

    def get(self, request, *args, **kwargs):
        self.subject_identifier = kwargs.get('subject_identifier')
        return super().get(request, *args, **kwargs)

    def pk_wrapper(self, obj):
        obj.str_pk = str(obj.id)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            dashboard_url=self.dashboard_url)
        return context
