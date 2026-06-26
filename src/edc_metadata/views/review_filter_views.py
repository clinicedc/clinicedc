from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from edc_data_manager.auth_objects import DATA_MANAGER_ROLE

from ..models import ReviewFilter


class SaveReviewFilterView(PermissionRequiredMixin, View):
    """POST: save the current board filter querystring under a name."""

    permission_required = "edc_metadata.view_crfmetadata"

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        name = (request.POST.get("name") or "").strip()
        query = request.POST.get("query") or ""
        shared = request.POST.get("shared") == "1"
        board = reverse("edc_metadata:manage_missing_url")
        if not name:
            messages.error(request, "Provide a name for the filter.")
        else:
            ReviewFilter.objects.update_or_create(
                user=request.user,
                name=name,
                defaults=dict(query=query, shared=shared),
            )
            messages.success(request, f'Saved filter "{name}".')
        return HttpResponseRedirect(f"{board}?{query}")


class DeleteReviewFilterView(PermissionRequiredMixin, View):
    """POST: delete a saved filter (own, or shared if a data manager)."""

    permission_required = "edc_metadata.view_crfmetadata"

    def post(self, request, *args, **kwargs):  # noqa: ARG002
        board = reverse("edc_metadata:manage_missing_url")
        obj = ReviewFilter.objects.filter(pk=request.POST.get("filter_id")).first()
        if obj and (obj.user_id == request.user.id or (obj.shared and self._is_dm(request))):
            name = obj.name
            obj.delete()
            messages.success(request, f'Deleted filter "{name}".')
        else:
            messages.error(request, "You cannot delete that filter.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER") or board)

    @staticmethod
    def _is_dm(request) -> bool:
        return request.user.userprofile.roles.filter(name=DATA_MANAGER_ROLE).exists()
