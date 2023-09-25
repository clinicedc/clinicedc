from __future__ import annotations

from urllib.parse import urlencode

from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_str
from edc_dashboard.url_names import InvalidUrlName, url_names


class ModelAdminRedirectOnDeleteMixin:

    """A mixin to redirect post delete.

    If `post_url_on_delete_name` and `post_full_url_on_delete` are
    not set, does nothing.
    """

    post_url_on_delete_name = "subject_dashboard_url"  # lookup key for url_names dict
    post_full_url_on_delete = None

    def __init__(self, *args):
        self.post_url_on_delete = None
        super().__init__(*args)

    def get_post_url_on_delete_name(self, request) -> str:
        return url_names.get(self.post_url_on_delete_name)

    def get_post_full_url_on_delete(self, request) -> str | None:
        return self.post_full_url_on_delete

    def get_post_url_on_delete(self, request, obj) -> str | None:
        """Returns a url for the redirect after delete."""
        post_url_on_delete = None
        querystring = urlencode(self.post_url_on_delete_querystring_kwargs(request, obj))
        if self.get_post_full_url_on_delete(request):
            post_url_on_delete = reverse(self.get_post_full_url_on_delete(request))
        else:
            try:
                url_name = self.get_post_url_on_delete_name(request)
            except InvalidUrlName:
                if self.post_url_on_delete_name:
                    raise
                url_name = None
            if url_name:
                kwargs = self.post_url_on_delete_kwargs(request, obj)
                post_url_on_delete = reverse(url_name, kwargs=kwargs)
        if post_url_on_delete and querystring:
            post_url_on_delete = f"{post_url_on_delete}?{querystring}"
        return post_url_on_delete

    def post_url_on_delete_kwargs(self, request, obj) -> dict:
        """Returns kwargs needed to reverse the url.

        Override.
        """
        return {}

    def post_url_on_delete_querystring_kwargs(self, request, obj) -> dict:
        """Returns kwargs for a querystring for the reversed url.

        Override.
        """
        return {}

    def delete_model(self, request, obj) -> None:
        """Overridden to intercept the obj to reverse
        the post_url_on_delete
        """
        self.post_url_on_delete = self.get_post_url_on_delete(request, obj)
        obj.delete()

    def response_delete(self, request, obj_display, obj_id):
        """Overridden to redirect to `post_url_on_delete`, if not None."""
        if self.post_url_on_delete:
            opts = self.model._meta
            msg = 'The %(name)s "%(obj)s" was deleted successfully.' % {
                "name": force_str(opts.verbose_name),
                "obj": force_str(obj_display),
            }
            messages.add_message(request, messages.SUCCESS, msg)
            return HttpResponseRedirect(self.post_url_on_delete)
        return super().response_delete(request, obj_display, obj_id)
