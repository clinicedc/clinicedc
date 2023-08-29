from __future__ import annotations

from django.urls import NoReverseMatch, reverse

from ..utils import get_value_from_lookup_string


class ModelAdminRedirectAllToChangelistMixinError(Exception):
    pass


class ModelAdminRedirectAllToChangelistMixin:
    """Redirects save, delete, cancel to the changelist.

    Overrides add/change views to intercept the post_save url and
    manipulate the redirect on cancel/delete.

    Important: Declare with ModelAdminNextUrlRedirectMixin and
        ModelAdminRedirectOnDeleteMixin.
    """

    changelist_url = None
    search_querystring_attr = "q"  # e.g ?q=12345
    change_search_field_name = None  # e.g. `screening_identifier` from model
    add_search_field_name = None

    def get_changelist_url(self, request):
        return self.changelist_url

    def redirect_url(self, request, obj, post_url_continue=None) -> str | None:
        if request.GET.dict().get(self.next_querystring_attr):
            return super().redirect_url(request, obj, post_url_continue=post_url_continue)
        return self.response_post_save_change(request, obj)

    def response_post_save_change(self, request, obj):
        try:
            url = reverse(self.get_changelist_url(request))
        except NoReverseMatch as e:
            raise ModelAdminRedirectAllToChangelistMixinError(e)
        value = get_value_from_lookup_string(self.change_search_field_name, obj=obj)
        if obj and value:
            url = f"{url}?q={value}"
        return url

    def get_post_full_url_on_delete(self, request):
        return self.get_changelist_url(request)

    def post_url_on_delete_querystring_kwargs(self, request, obj) -> dict:
        q = get_value_from_lookup_string(self.change_search_field_name, obj=obj)
        return dict(q=q)

    def add_view(self, request, form_url="", extra_context=None):
        q = get_value_from_lookup_string(
            self.add_search_field_name, request=request
        ) or get_value_from_lookup_string(self.change_search_field_name, request=request)
        extra_context = extra_context or {}
        extra_context.update(
            cancel_url=self.get_changelist_url(request), cancel_url_querystring_data={"q": q}
        )
        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        q = get_value_from_lookup_string(
            self.change_search_field_name,
            obj=self.model.objects.get(id=object_id),
        )
        extra_context = extra_context or {}
        extra_context.update(
            cancel_url=self.get_changelist_url(request), cancel_url_querystring_data={"q": q}
        )
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )
