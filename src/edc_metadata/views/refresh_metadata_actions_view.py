from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import SUCCESS
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from edc_dashboard import url_names
from edc_utils import get_utcnow
from edc_utils.round_up import round_half_away_from_zero
from edc_visit_tracking.utils import get_subject_visit_model_cls


class RefreshMetadataActionsView(LoginRequiredMixin, View):
    """A view to refresh metadata.

    For example, add to urls:
        path(
            "refresh_subject_dashboard/<str:subject_visit_id>",
            RefreshMetadataActionsView.as_view(),
            name="refresh_metadata_actions_url",
        )
    """

    @staticmethod
    def refresh_metadata(subject_visit_id=None, **kwargs):  # noqa
        """Save related visit model instance to run metadata update."""
        related_visit = get_subject_visit_model_cls().objects.get(id=subject_visit_id)
        related_visit.save()
        related_visit.refresh_from_db()
        return related_visit

    def get(self, request, *args, **kwargs):
        dte1 = get_utcnow()
        related_visit = self.refresh_metadata(**kwargs)
        url_name = url_names.get("subject_dashboard_url")
        args = (
            related_visit.appointment.subject_identifier,
            str(related_visit.appointment.id),
        )
        url = reverse(url_name, args=args)
        messages.add_message(
            request,
            SUCCESS,
            f"The data collection schedule for {related_visit.visit_code}."
            f"{related_visit.visit_code_sequence} has been refreshed "
            f"({round_half_away_from_zero((get_utcnow()-dte1).microseconds/1000000, 2)} "
            "seconds)",
        )
        return HttpResponseRedirect(url)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
