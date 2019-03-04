from django.views.generic.base import ContextMixin
from django.urls.base import reverse

from ..dashboard_urls import dashboard_urls


class FormActionViewError(Exception):
    pass


class FormActionViewMixin(ContextMixin):

    action_name = None
    form_action_name = "form_action"
    form_action_selected_items_name = "selected_items"
    form_action_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            action_name=self.action_name,
            form_action_name=self.form_action_name,
            form_action_selected_items_name=self.form_action_selected_items_name,
            form_action_url_reversed=self.form_action_url_reversed,
        )
        return context

    @property
    def form_action_url_kwargs(self):
        return self.url_kwargs

    @property
    def form_action_url_reversed(self):
        try:
            form_action_url = dashboard_urls[self.form_action_url]
        except KeyError:
            raise FormActionViewError(
                f"'form_action_url' not defined in dashboard_urls. "
                f"See {repr(self)}. Got {self.form_action_url}"
            )
        return reverse(form_action_url, kwargs=self.form_action_url_kwargs)
