import urllib

from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.text import slugify
from django.views.generic.base import TemplateView
from edc_dashboard.url_names import url_names

from ...dashboard_templates import dashboard_templates


class InvalidPostError(Exception):
    pass


class ActionViewError(Exception):
    pass


class ActionView(TemplateView):

    """A view for lab "actions" such as receive, process,
    aliquot, etc.
    """

    form_action_selected_items_name = "selected_items"
    post_action_url = None  # key exists in url_names
    redirect_querystring = {}
    template_name = dashboard_templates.get("home_template")
    valid_form_actions = []

    navbar_name = "specimens"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_items = []
        self.action = None

    def process_form_action(self, request=None):
        """Override to conditionally handle the action POST attr."""
        pass

    @property
    def selected_items(self):
        """Returns a list of selected listboard items."""
        if not self._selected_items:
            self._selected_items = (
                self.request.POST.getlist(self.form_action_selected_items_name) or []
            )
            self._selected_items = [x for x in self._selected_items if x]
        return self._selected_items

    @property
    def url_kwargs(self):
        """Returns the default dictionary to reverse the post url."""
        return {}

    def post(self, request, *args, **kwargs):
        """Process the form "action" then redirect."""
        action = slugify(self.request.POST.get("action", "").lower())
        if action not in self.valid_form_actions:
            raise InvalidPostError(f"Invalid form action in POST. Got {action}")
        else:
            self.action = action
        self.process_form_action(request=request)
        url_name = url_names.get(self.post_action_url)
        url = reverse(url_name, kwargs=self.url_kwargs)
        if self.redirect_querystring:
            url = f"{url}?{urllib.parse.urlencode(self.redirect_querystring)}"
        return HttpResponseRedirect(url)
