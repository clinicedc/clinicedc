from django.urls.base import reverse
from django.views.generic.base import ContextMixin
from edc_dashboard.url_names import url_names


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
        form_action_url = url_names.get(self.form_action_url)
        return reverse(form_action_url, kwargs=self.form_action_url_kwargs)
