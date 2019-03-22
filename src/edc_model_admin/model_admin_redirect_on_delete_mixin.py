from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_text


class ModelAdminRedirectOnDeleteMixin:

    """A mixin to redirect on delete.

    If `post_url_on_delete_name` is not set, does nothing.
    """

    post_url_on_delete_name = None

    def get_post_url_on_delete(self, request, obj):
        url_name = self.get_post_url_on_delete_name(request, obj)
        if url_name:
            kwargs = self.post_url_on_delete_kwargs(request, obj)
            post_url_on_delete = reverse(url_name, kwargs=kwargs)
            return post_url_on_delete
        return None

    def get_post_url_on_delete_name(self, request, obj):
        """Returns the urlname or namespace:urlname.

        Gets the urlname from url_name_data in the request object
        using `post_url_on_delete_name` as the dict key (if using
        Dashboard Middleware). If that fails, falls back to return
        `post_url_on_delete_name` as the urlname.
        """
        try:
            url_name = request.url_name_data.get(self.post_url_on_delete_name)
        except AttributeError:
            url_name = None
        return url_name or self.post_url_on_delete_name

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
            msg = ('The %(name)s "%(obj)s" was deleted successfully.') % {
                "name": force_text(opts.verbose_name),
                "obj": force_text(obj_display),
            }
            messages.add_message(request, messages.SUCCESS, msg)
            return HttpResponseRedirect(self.post_url_on_delete)
        return super().response_delete(request, obj_display, obj_id)
