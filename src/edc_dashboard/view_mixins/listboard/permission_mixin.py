import six

from django.http import Http404
from django.utils.translation import gettext as _


class ListboardPermmissionMixin:

    permissions_warning_message = "You do not have permission to view these data."

    # e.g. "edc_dashboard.view_subject_listboard"
    listboard_view_permission_codename = None

    # e.g. "edc_dashboard.view_subject_listboard"
    listboard_view_only_my_permission_codename = None

    def get(self, request, *args, **kwargs):
        if not self.has_view_listboard_perms:
            raise Http404(
                _(
                    "You do not have sufficient user or "
                    "group permissions to view this page."
                )
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            has_listboard_model_perms=self.has_listboard_model_perms,
            has_view_listboard_perms=self.has_view_listboard_perms,
            listboard_view_permission_codename=self.listboard_view_permission_codename,
            permissions_warning_message=self.permissions_warning_message,
        )
        return context

    def get_queryset(self):
        """Return the queryset for this view.

        Completely overrides ListBoardView.get_queryset.

        Note:
            the resulting queryset filtering takes allocated
            permissions into account using Django's permissions
            framework.

            Only returns records if user has dashboard permissions to
            do so. See `has_view_listboard_perms`.

            Limits records to those created by the current user if
            `has_view_only_my_listboard_perms` return True.
            See `has_view_only_my_listboard_perms`.

        Passes filter/exclude criteria to `get_filtered_queryset`.

        Note: The returned queryset is set to self.object_list in
        `get()` just before rendering to response.
        """
        queryset = getattr(
            self.listboard_model_cls, self.listboard_model_manager_name
        ).none()
        if self.has_view_listboard_perms:
            filter_options = self.get_queryset_filter_options(
                self.request, *self.args, **self.kwargs
            )
            if self.has_view_only_my_listboard_perms:
                filter_options.update(user_created=self.request.user.username)
            exclude_options = self.get_queryset_exclude_options(
                self.request, *self.args, **self.kwargs
            )
            queryset = self.get_filtered_queryset(
                filter_options=filter_options, exclude_options=exclude_options
            )
            ordering = self.get_ordering()
            if ordering:
                if isinstance(ordering, six.string_types):
                    ordering = (ordering,)
                queryset = queryset.order_by(*ordering)
        return queryset

    @property
    def has_view_listboard_perms(self):
        """Returns True if request.user has permissions to
        view the listboard.

        If False, `get_queryset` returns an empty queryset.
        """
        return self.request.user.has_perms([self.listboard_view_permission_codename])

    @property
    def has_view_only_my_listboard_perms(self):
        """Returns True if request.user ONLY has permissions to
        view records created by request.user on the listboard.
        """
        return self.request.user.has_perm(
            self.listboard_view_only_my_permission_codename
        )

    @property
    def has_listboard_model_perms(self):
        """Returns True if request.user has permissions to
        add/change the listboard model.

        Does not affect `get_queryset`.

        Used in templates.
        """
        app_label = self.listboard_model_cls._meta.label_lower.split(".")[0]
        model_name = self.listboard_model_cls._meta.label_lower.split(".")[1]
        return self.request.user.has_perms(
            f"{app_label}.add_{model_name}", f"{app_label}.change_{model_name}"
        )
