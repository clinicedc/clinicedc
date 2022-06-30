from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from django.utils.html import format_html

from edc_data_manager.auth_objects import DATA_MANAGER_ROLE


class DataManagerModelAdminMixin:
    def get_queryset(self, request):
        """
        Return a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        expanded_view_roles = getattr(
            settings, "EDC_DATA_MANAGER_EXPANDED_VIEW_ROLES", [DATA_MANAGER_ROLE]
        )
        storage = get_messages(request)
        roles = " ".join(expanded_view_roles)
        my_message = format_html(
            "Your are being shown data from all sites but will only be able to change "
            "data for the current site. To view data for one site, use the 'By site' "
            "filter on the right sidebar. This feature is enabled because you are a "
            f"member of one of these roles: <i>{roles}</i>.",
            fail_silently=True,
        )
        if not [message for message in storage if message.message == my_message]:
            messages.warning(request, my_message)

        roles = [r.name for r in request.user.userprofile.roles.all()]
        if list(set(expanded_view_roles) & set(roles)):
            site_ids = [s.id for s in request.user.userprofile.sites.all()]
            qs = self.model.objects.get_queryset().filter(site_id__in=site_ids)
        else:
            qs = self.model._default_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
