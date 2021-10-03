from django.conf import settings

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
