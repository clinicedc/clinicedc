from __future__ import annotations

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView
from edc_constants.constants import CONFIRMED
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin

from ..constants import ALREADY_CONFIRMED, INVALID
from ..models import Stock
from ..utils import confirm_stock


@method_decorator(login_required, name="dispatch")
class ConfirmStockFromQuerySetView(
    EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView
):
    template_name: str = "edc_pharmacy/stock/confirm_stock_by_queryset.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"
    codes_per_page = 12

    def get_context_data(self, **kwargs):
        context = dict(
            CONFIRMED=CONFIRMED,
            ALREADY_CONFIRMED=ALREADY_CONFIRMED,
            INVALID=INVALID,
            item_count=list(range(1, self.adjusted_unconfirmed_count + 1)),
            unconfirmed_count=self.unconfirmed_count,
            confirmed_count=self.confirmed_count,
            source_changelist_url=self.source_changelist_url,
            **self.session_data,
        )
        return context

    @property
    def session_data(self):
        session_uuid = self.kwargs.get("session_uuid")
        session_data = {}
        if session_uuid:
            session_obj = self.request.session[str(session_uuid)]
            transaction_word = _(session_obj.get("transaction_word") or "confirmed")
            last_stock_codes = [
                [x, CONFIRMED, transaction_word]
                for x in session_obj.get("confirmed_codes") or []
            ]
            last_stock_codes.extend(
                [
                    [
                        x,
                        ALREADY_CONFIRMED,
                        _(
                            "already %(transaction_word)s"
                            % {"transaction_word": transaction_word}
                        ),
                    ]
                    for x in session_obj.get("already_confirmed_codes") or []
                ]
            )
            last_stock_codes.extend(
                [[x, INVALID, _("invalid")] for x in session_obj.get("invalid_codes") or []]
            )
            session_data = dict(
                transaction_word=session_obj.get("transaction_word"),
                source_pk=session_obj.get("source_pk"),
                source_identifier=session_obj.get("source_identifier"),
                source_label_lower=session_obj.get("source_label_lower"),
                source_model_name=session_obj.get("source_model_name"),
                last_stock_codes=last_stock_codes,
                stock_codes=session_obj.get("stock_codes") or [],
                total_stock_code_count=len(session_obj.get("stock_codes")),
            )
        return session_data

    @property
    def unconfirmed_count(self) -> int:
        return (
            Stock.objects.values("code")
            .filter(
                code__in=self.session_data.get("stock_codes"),
                confirmation__isnull=True,
            )
            .count()
        )

    @property
    def confirmed_count(self) -> int:
        return (
            Stock.objects.values("code")
            .filter(
                code__in=self.session_data.get("stock_codes"),
                confirmation__isnull=False,
            )
            .count()
        )

    @property
    def adjusted_unconfirmed_count(self) -> int:
        return (
            self.codes_per_page
            if self.unconfirmed_count > self.codes_per_page
            else self.unconfirmed_count
        )

    @property
    def source_changelist_url(self):
        model = self.session_data.get("source_label_lower").split(".")[1]
        return reverse(f"edc_pharmacy_admin:edc_pharmacy_{model}_changelist")

    @property
    def source_model_cls(self):
        label_lower = self.session_data.get("source_label_lower")
        return django_apps.get_model(label_lower)

    def post(self, request, *args, **kwargs):
        stock_codes = request.POST.getlist("stock_codes")
        if len(stock_codes) != len(list(set(stock_codes))):
            messages.add_message(
                request,
                messages.ERROR,
                (
                    "Stock items not confirmed. List of stock codes "
                    "is not unique. Please check and scan again."
                ),
            )
            url = reverse("edc_pharmacy:confirm_stock_from_queryset_url", kwargs=kwargs)
        else:
            confirmed_codes, already_confirmed_codes, invalid_codes = confirm_stock(
                None,
                stock_codes,
                None,
                confirmed_by=request.user.username,
                user_created=request.user.username,
            )
            if confirmed_codes:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Successfully confirmed {len(confirmed_codes)} stock items. ",
                )
            if already_confirmed_codes:
                messages.add_message(
                    request,
                    messages.WARNING,
                    (
                        f"Skipped {len(already_confirmed_codes)} items. Stock items are "
                        "already confirmed."
                    ),
                )
            if invalid_codes:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Invalid codes submitted! Got {', '.join(invalid_codes)} .",
                )

            if (
                Stock.objects.values("code")
                .filter(
                    code__in=self.session_data.get("stock_codes"),
                    confirmation__isnull=True,
                )
                .exists()
            ):
                self.request.session[str(self.kwargs.get("session_uuid"))] = dict(
                    confirmed_codes=confirmed_codes,
                    already_confirmed_codes=already_confirmed_codes,
                    invalid_codes=invalid_codes,
                    source_pk=self.session_data.get("source_pk"),
                    source_identifier=self.session_data.get("source_identifier"),
                    source_label_lower=self.session_data.get("source_label_lower"),
                    source_model_name=self.session_data.get("source_model_name"),
                    stock_codes=self.session_data.get("stock_codes"),
                )
                url = reverse("edc_pharmacy:confirm_stock_from_queryset_url", kwargs=kwargs)
            else:
                self.request.session[self.kwargs.get("session_uuid")] = None
                url = f"{self.source_changelist_url}?q="
        return HttpResponseRedirect(url)
