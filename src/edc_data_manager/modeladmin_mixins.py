from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .auth_objects import DATA_MANAGER_ROLE

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin


class DataManagerSiteModelAdminMixin:
    """Do not declare together with `SiteModelAdminMixin`"""

    on_site_manager = "on_site"

    def get_queryset(self: ModelAdmin, request):
        """
        Return a QuerySet of all model instances for multiple sites
        that can be viewed/edited by the admin site. This is used
        by changelist_view.
        """
        expanded_view_roles = getattr(
            settings, "EDC_DATA_MANAGER_EXPANDED_VIEW_ROLES", [DATA_MANAGER_ROLE]
        )
        roles = " ".join(expanded_view_roles)
        my_message = format_html(
            "You are being shown view only data from multiple sites. Add/change permissions, "
            "if you have them, apply to the current site only. This feature is enabled "
            "because you are a member of one of these roles: <i>{}</i>.",
            mark_safe(roles),  # nosec B308, B703
        )
        roles = [r.name for r in request.user.userprofile.roles.all()]
        if list(set(expanded_view_roles) & set(roles)):
            site_ids = [s.id for s in request.user.userprofile.sites.all()]
            qs = self.model._default_manager.get_queryset().filter(site_id__in=site_ids)
            storage = get_messages(request)
            if not [message for message in storage if message.message == my_message]:
                self.message_user(
                    request=request,
                    message=my_message,
                    level=messages.INFO,
                    fail_silently=True,
                )
        else:
            manager = self.on_site_manager or "_default_manager"
            qs = getattr(self.model, manager).get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
