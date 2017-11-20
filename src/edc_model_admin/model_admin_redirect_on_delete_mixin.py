from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls import reverse, NoReverseMatch
from django.utils.encoding import force_text


class ModelAdminRedirectOnDeleteMixin:

    """A mixin to redirect on delete.
    """
    post_url_on_delete_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_url_on_delete = None

    def post_url_on_delete_kwargs(self, request, obj):
        """Returns kwargs needed to reverse the post_url,
        `post_url_on_delete_name`.

        Override.
        """
        return {}

    def delete_model(self, request, obj):
        """Overridden to intercept the obj to reverse the post_url
        if `post_url_on_delete_name` is not None.
        """
        if self.post_url_on_delete_name:
            kwargs = self.post_url_on_delete_kwargs(request, obj)
            try:
                self.post_url_on_delete = reverse(
                    self.post_url_on_delete_name,
                    kwargs=kwargs)
            except NoReverseMatch:
                pass
        obj.delete()

    def response_delete(self, request, obj_display, obj_id):
        """Overridden to redirect to `post_url_on_delete`, if not None.
        """
        if self.post_url_on_delete:
            opts = self.model._meta
            msg = ('The %(name)s "%(obj)s" was deleted successfully.') % {
                'name': force_text(opts.verbose_name),
                'obj': force_text(obj_display)}
            messages.add_message(request, messages.SUCCESS, msg)
            return HttpResponseRedirect(self.post_url_on_delete)
        return super().response_delete(request, obj_display, obj_id)
