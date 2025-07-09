from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin
from edc_utils import get_utcnow

from ..models import ConfirmationAtSite, Formulation, Location, Rx
from ..utils import dispense


@method_decorator(login_required, name="dispatch")
class DispenseView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    model_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/dispense.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"

    def get_context_data(self, **kwargs):
        container_count = self.kwargs.get("container_count") or 0
        location_id = self.kwargs.get("location_id")
        formulation_id = self.kwargs.get("formulation_id")
        try:
            location = Location.objects.get(pk=location_id)
        except ObjectDoesNotExist:
            location = None
        try:
            formulation = Formulation.objects.get(pk=formulation_id)
        except ObjectDoesNotExist:
            formulation = None
        kwargs.update(
            item_count=list(range(1, container_count + 1)),
            locations=Location.objects.filter(site__isnull=False),
            formulations=Formulation.objects.all(),
            location=location,
            formulation=formulation,
        )
        return super().get_context_data(**kwargs)

    def get_rx(self, subject_identifier, location, formulation) -> Rx | None:
        try:
            rx = Rx.objects.get(
                registered_subject__subject_identifier=subject_identifier,
                medications__in=[formulation.medication],
                site=getattr(location, "site", None),
            )
        except ObjectDoesNotExist:
            rx = None
            messages.add_message(
                self.request,
                messages.WARNING,
                f"Subject {subject_identifier} not found at {location.display_name}.",
            )
        else:
            if rx.rx_expiration_date and rx.rx_expiration_date < get_utcnow():
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    (
                        f"The prescription for {formulation} for "
                        f"subject {subject_identifier} is expired."
                    ),
                )
                rx = None
        return rx

    @property
    def confirmation_at_site(self):
        confirmation_at_site_id = self.kwargs.get("confirmation_at_site")
        try:
            confirmation_at_site = ConfirmationAtSite.objects.get(id=confirmation_at_site_id)
        except ObjectDoesNotExist:
            confirmation_at_site = None
            messages.add_message(
                self.request, messages.ERROR, "Invalid stock transfer confirmation."
            )
        return confirmation_at_site

    def post(self, request, *args, **kwargs):
        location_id = request.POST.get("location_id")
        location = Location.objects.get(pk=location_id)
        formulation_id = request.POST.get("formulation_id")
        formulation = Formulation.objects.get(pk=formulation_id)
        subject_identifier = request.POST.get("subject_identifier")
        container_count = request.POST.get("container_count")
        stock_codes = request.POST.getlist("codes") if request.POST.get("codes") else None
        rx = self.get_rx(subject_identifier, location, formulation)
        if not stock_codes and location and formulation and rx and container_count:
            url = reverse(
                "edc_pharmacy:dispense_url",
                kwargs={
                    "location_id": location.id,
                    "formulation_id": formulation.id,
                    "subject_identifier": subject_identifier,
                    "container_count": container_count,
                },
            )
            return HttpResponseRedirect(url)

        elif stock_codes and location and formulation and rx and container_count:
            dispense_qs = dispense(
                stock_codes,
                location,
                rx,
                request.user.username,
                request,
            )
            if dispense_qs:
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    f"Dispensed {dispense_qs.count()} item.",
                )
            url = reverse(
                "edc_pharmacy:dispense_url",
                kwargs={
                    "location_id": location.id,
                    "formulation_id": formulation.id,
                    "subject_identifier": subject_identifier,
                    "container_count": container_count,
                },
            )
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(reverse("edc_pharmacy:home_url"))
