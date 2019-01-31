from django.http.response import HttpResponseRedirect


class BaseModelAdminRedirectMixin:

    """Redirect on add, change, or delete.
    """

    def redirect_url(self, request, obj, post_url_continue=None):
        return None

    def redirect_url_on_add(self, request, obj, post_url_continue=None):
        return self.redirect_url(request, obj, post_url_continue=post_url_continue)

    def redirect_url_on_change(self, request, obj, post_url_continue=None):
        return self.redirect_url(request, obj, post_url_continue=post_url_continue)

    def redirect_url_on_delete(self, request, obj_display, obj_id):
        return None

    def response_add(self, request, obj, post_url_continue=None):
        redirect_url = None
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            redirect_url = self.redirect_url_on_add(request, obj)
        if redirect_url:
            return HttpResponseRedirect(redirect_url)
        return super().response_add(request, obj, post_url_continue=post_url_continue)

    def response_change(self, request, obj):
        redirect_url = None
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            redirect_url = self.redirect_url_on_change(request, obj)
        if redirect_url:
            return HttpResponseRedirect(redirect_url)
        return super().response_change(request, obj)

    def response_delete(self, request, obj_display, obj_id):
        redirect_url = self.redirect_url_on_delete(request, obj_display, obj_id)
        if redirect_url:
            return HttpResponseRedirect(redirect_url)
        return super().response_delete(request, obj_display, obj_id)
