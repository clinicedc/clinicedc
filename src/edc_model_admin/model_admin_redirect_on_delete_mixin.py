from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_str
from edc_dashboard.url_names import url_names, InvalidUrlName


class ModelAdminRedirectOnDeleteMixin:

    """A mixin to redirect on delete.

    If `post_url_on_delete_name` is not set, does nothing.
    """

    post_url_on_delete_name = None  # lookup key for url_names dict

    def get_post_url_on_delete(self, request, obj):
        try:
            url_name = url_names.get(self.post_url_on_delete_name)
        except InvalidUrlName:
            if self.post_url_on_delete_name:
                raise
            url_name = None
        if url_name:
            kwargs = self.post_url_on_delete_kwargs(request, obj)
            post_url_on_delete = reverse(url_name, kwargs=kwargs)
            return post_url_on_delete
        return None

    def post_url_on_delete_kwargs(self, request, obj):
        """Returns kwargs needed to reverse the url.

        Override.
        """
        return {}

    def delete_model(self, request, obj):
        """Overridden to intercept the obj to reverse
        the post_url_on_delete
        """
        self.post_url_on_delete = self.get_post_url_on_delete(request, obj)
        obj.delete()

    def response_delete(self, request, obj_display, obj_id):
        """Overridden to redirect to `post_url_on_delete`, if not None.
        """
        if self.post_url_on_delete:
            opts = self.model._meta
            msg = 'The %(name)s "%(obj)s" was deleted successfully.' % {
                "name": force_str(opts.verbose_name),
                "obj": force_str(obj_display),
            }
            messages.add_message(request, messages.SUCCESS, msg)
            return HttpResponseRedirect(self.post_url_on_delete)
        return super().response_delete(request, obj_display, obj_id)
