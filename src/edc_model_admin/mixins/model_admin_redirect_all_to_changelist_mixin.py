from __future__ import annotations

from django.urls import reverse


class ModelAdminRedirectAllToChangelistMixin:
    """Redirects save, delete, cancel to the changelist.

    Overrides add/change views to intercept the post_save url and
    manipulate the redirect on cancel/delete.

    Declare with ModelAdminNextUrlRedirectMixin and
    ModelAdminRedirectOnDeleteMixin.
    """

    changelist_url = None
    search_querystring_attr = "q"  # e.g ?q=12345
    search_field_name = None  # e.g. `screening_identifier` from model

    def redirect_url(self, request, obj, post_url_continue=None) -> str | None:
        if request.GET.dict().get(self.next_querystring_attr):
            return super().redirect_url(request, obj, post_url_continue=post_url_continue)
        return self.response_post_save_change(request, obj)

    def response_post_save_change(self, request, obj):
        url = reverse(self.changelist_url)
        if obj:
            return f"{url}?q={getattr(obj, self.search_field_name)}"
        return url

    @property
    def post_full_url_on_delete(self):
        return self.changelist_url

    def post_url_on_delete_querystring_kwargs(self, request, obj) -> dict:
        return dict(q=getattr(obj, self.search_field_name))

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            cancel_url=self.changelist_url,
            cancel_url_querystring_data={"q": request.GET.get(self.search_field_name)},
        )
        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            cancel_url=self.changelist_url,
            cancel_url_querystring_data={
                "q": getattr(self.model.objects.get(id=object_id), self.search_field_name)
            },
        )
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )
