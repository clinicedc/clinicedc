from django.views.generic.base import TemplateView


class ListboardMixin(TemplateView):

    listboard_url_name = 'home_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(listboard_url_name=self.listboard_url_name)
        return context
