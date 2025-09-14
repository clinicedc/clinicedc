from __future__ import annotations

from typing import Any

from django.apps import apps as django_apps
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.translation import gettext as _
from django.views.generic.list import ListView

from edc_dashboard.view_mixins import (
    TemplateRequestContextMixin,
    UrlRequestContextMixin,
)
from edc_sites.site import sites
from edc_sites.view_mixins import SiteViewMixin

from ..view_mixins import QueryStringViewMixin, SearchListboardMixin


class ListboardViewError(Exception):
    pass


class BaseListboardView(SiteViewMixin, TemplateRequestContextMixin, ListView):
    listboard_model: str | None = None  # label_lower model name
    context_object_name: str = "results"

    empty_queryset_message: str = _("Nothing to display.")

    listboard_template: str | None = None  # an existing key in request.context_data

    # if self.listboard_url declared through another mixin.
    listboard_url: str | None = None  # an existing key in request.context_data
    listboard_back_url: str | None = None

    # styling
    # default, info, success, danger, warning, etc. See Bootstrap.
    listboard_panel_style: str = "default"
    listboard_fa_icon: str | None = None
    listboard_panel_title: str | None = None
    listboard_instructions: str | None = None
    show_change_form_button: bool = True

    # permissions
    permissions_warning_message: str = _("You do not have permission to view these data.")
    # e.g. "edc_subject_dashboard.view_subject_listboard"
    listboard_view_permission_codename: str | None = None
    # e.g. "edc_subject_dashboard.view_subject_listboard"
    listboard_view_only_my_permission_codename: str | None = None

    ordering: str = "-created"

    orphans: int = 3
    paginate_by: int = 10
    paginator_url = None  # defaults to listboard_url

    def get(self, request, *args, **kwargs):
        if not self.has_view_listboard_perms:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        if self.listboard_fa_icon and self.listboard_fa_icon.startswith("fa-"):
            self.listboard_fa_icon = f"fas {self.listboard_fa_icon}"
        kwargs.update(
            empty_queryset_message=self.get_empty_queryset_message(),
            listboard_fa_icon=self.listboard_fa_icon,
            listboard_panel_style=self.listboard_panel_style,
            listboard_panel_title=self.listboard_panel_title,
            listboard_instructions=self.listboard_instructions,
            show_change_form_button=self.show_change_form_button,
            # object_list=self.object_list,
            **self.add_url_to_context(
                new_key="listboard_url", existing_key=self.listboard_url
            ),
        )
        if self.listboard_back_url:
            kwargs.update(
                **self.add_url_to_context(
                    new_key="listboard_back_url",
                    existing_key=self.listboard_back_url,
                )
            )
        kwargs.update(
            has_listboard_model_perms=self.has_listboard_model_perms,
            has_view_listboard_perms=self.has_view_listboard_perms,
            listboard_view_permission_codename=self.listboard_view_permission_codename,
            permissions_warning_message=self.permissions_warning_message,
            **self.add_url_to_context(
                new_key="paginator_url",
                existing_key=self.paginator_url or self.listboard_url,
            ),
        )
        return super().get_context_data(**kwargs)

    def get_template_names(self):
        return [self.get_template_from_context(self.listboard_template)]

    @property
    def url_kwargs(self):
        """Returns a dictionary of URL options for either the
        Search form URL and the Form Action.
        """
        return {}

    def get_listboard_model(self) -> str:
        return self.listboard_model

    @property
    def listboard_model_cls(self):
        """Returns the listboard's model class.

        Accepts `listboard_model` as a model class or label_lower.
        """
        if not self.get_listboard_model():
            raise ListboardViewError(f"Listboard model not declared. Got None. See {self!r}")
        try:
            return django_apps.get_model(self.get_listboard_model())
        except (ValueError, AttributeError):
            return self.get_listboard_model()

    def get_queryset(self):
        """Return the queryset for this view.

        Completely overrides ListView.get_queryset.

        The returned queryset is set to self.object_list in the
        parent call to `get()` just before rendering to response.

        Note:
            the resulting queryset filtering takes allocated
            permissions into account using Django's permissions
            framework.

            Only returns records if user has dashboard permissions to
            do so. See `has_view_listboard_perms`.

            Limit records to those created by the current user if
            `has_view_only_my_listboard_perms` return True.
            See `has_view_only_my_listboard_perms`.

        Applies additional filter/exclude criteria.
        """

        queryset = self.listboard_model_cls.objects.none()
        if self.has_view_listboard_perms:
            q_exclude, opts_exclude = self.get_queryset_exclude_options(
                self.request, *self.args, **self.kwargs
            )
            q_filter, opts_filter = self.get_queryset_filter_options(
                self.request, *self.args, **self.kwargs
            )

            queryset = self.listboard_model_cls.objects.filter(
                q_filter, **opts_filter
            ).exclude(q_exclude, **opts_exclude)

            queryset = self.get_updated_queryset(queryset)

            ordering = self.get_ordering()
            if ordering:
                if isinstance(ordering, (str,)):
                    ordering = (ordering,)
                queryset = queryset.order_by(*ordering)
        return queryset

    def get_queryset_filter_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        """Returns filtering applied to every queryset"""
        options = dict(site_id__in=sites.get_site_ids_for_user(request=self.request))
        if self.has_view_only_my_listboard_perms:
            options.update(user_created=self.request.user.username)
        return Q(), options

    def get_queryset_exclude_options(self, request, *args, **kwargs) -> tuple[Q, dict]:
        """Returns exclude options applied to every queryset"""
        return Q(), {}

    def get_empty_queryset_message(self) -> str:
        return self.empty_queryset_message

    def get_updated_queryset(self, queryset):
        """Return the queryset for this view.

        Hook for a last chance to modify the queryset
        before ordering.
        """
        return queryset

    @property
    def has_view_listboard_perms(self):
        """Returns True if request.user has permissions to
        view the listboard.

        If False, `get_queryset` returns an empty queryset.
        """
        return self.request.user.has_perm(self.listboard_view_permission_codename)

    @property
    def has_view_only_my_listboard_perms(self):
        """Returns True if `request.user` ONLY has permissions to
        view records created by `request.user` on the listboard.
        """
        return self.request.user.has_perm(self.listboard_view_only_my_permission_codename)

    @property
    def has_listboard_model_perms(self):
        """Returns True if `request.user` has permissions to
        add/change the listboard model.

        Does not affect `get_queryset`.

        Used in templates.
        """
        app_label = self.listboard_model_cls._meta.label_lower.split(".")[0]
        model_name = self.listboard_model_cls._meta.label_lower.split(".")[1]
        return self.request.user.has_perms(
            [f"{app_label}.add_{model_name}", f"{app_label}.change_{model_name}"]
        )


class ListboardView(
    QueryStringViewMixin,
    UrlRequestContextMixin,
    SearchListboardMixin,
    BaseListboardView,
):
    urlconfig_getattr = "listboard_urls"

    @classmethod
    def get_urlname(cls):
        return cls.listboard_url
