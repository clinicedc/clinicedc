from __future__ import annotations

import ast

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin
from edc_protocol.view_mixins import EdcProtocolViewMixin
from edc_utils import get_utcnow

from ..exceptions import AllocationError, InsufficientStockError
from ..models import Assignment, Stock, StockRequest, StockRequestItem
from ..utils import allocate_stock


@method_decorator(login_required, name="dispatch")
class AllocateToSubjectView(EdcViewMixin, NavbarViewMixin, EdcProtocolViewMixin, TemplateView):
    model_pks: list[str] | None = None
    template_name: str = "edc_pharmacy/stock/allocate_to_subject.html"
    navbar_name = settings.APP_NAME
    navbar_selected_item = "pharmacy"
    items_per_page = 12

    def get_context_data(self, **kwargs):
        remaining_count, total_count = self.get_counts(self.stock_request)
        show_count = (
            self.items_per_page if remaining_count >= self.items_per_page else remaining_count
        )
        kwargs.update(
            stock_request=self.stock_request,
            assignment=self.selected_assignment,
            stock_request_changelist_url=self.stock_request_changelist_url,
            subject_identifiers=self.get_next_subject_identifiers(self.items_per_page),
            subject_identifiers_count=self.subject_identifiers.count(),
            assignments=Assignment.objects.all().order_by("name"),
            remaining_count=remaining_count,
            total_count=total_count,
            show_count=show_count,
            SHORT_DATE_FORMAT=settings.SHORT_DATE_FORMAT,
        )
        return super().get_context_data(**kwargs)

    @property
    def subject_identifiers(self):
        """Returns a queryset of unallocated stock request
        items for the given assignment.
        """
        return (
            StockRequestItem.objects.values_list(
                "registered_subject__subject_identifier", flat=True
            )
            .filter(
                stock_request=self.stock_request,
                allocation__isnull=True,
                assignment=self.selected_assignment,
            )
            .order_by("appt_datetime", "registered_subject__subject_identifier")
        )

    @property
    def stock_request(self):
        stock_request_id = self.kwargs.get("stock_request")
        try:
            stock_request = StockRequest.objects.get(id=stock_request_id)
        except ObjectDoesNotExist:
            stock_request = None
            messages.add_message(self.request, messages.ERROR, "Invalid stock request.")
        return stock_request

    @property
    def selected_assignment(self):
        assignment_id = self.kwargs.get("assignment")
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except ObjectDoesNotExist:
            assignment = None
        return assignment

    def get_next_subject_identifiers(self, count: int | None = None) -> list[str]:
        if self.selected_assignment:
            subject_identifiers = self.subject_identifiers
            if count:
                return [s for s in subject_identifiers[:count]]
            return [s for s in subject_identifiers]
        return []

    @property
    def stock_request_changelist_url(self) -> str:
        if self.stock_request:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist")
            url = f"{url}?q={self.stock_request.request_identifier}"
            return url
        return "/"

    @staticmethod
    def get_assignment(assignment_id) -> Assignment | None:
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except ObjectDoesNotExist:
            assignment = None
        return assignment

    def redirect_on_has_duplicates(
        self, stock_codes: list[str], stock_request: StockRequest, assignment: Assignment
    ) -> str | None:
        if len(stock_codes or []) != len(list(set(stock_codes or []))):
            messages.add_message(
                self.request,
                messages.ERROR,
                "Nothing saved. Duplicate codes detected in list. Please try again.",
            )
            url = reverse(
                "edc_pharmacy:allocate_url",
                kwargs={
                    "stock_request": stock_request.id,
                    "assignment": assignment.id,
                },
            )
            return url
        return None

    def redirect_on_uncomfirmed_stock_codes(
        self, stock_codes: list[str], stock_request: StockRequest, assignment: Assignment
    ) -> str | None:
        if stock_codes:
            confirmed_codes = Stock.objects.filter(
                code__in=stock_codes,
                confirmation__isnull=False,
            ).values_list("code", flat=True)
            if len(confirmed_codes) != len(stock_codes):
                uncomfirmed_codes = ", ".join(
                    [code for code in stock_codes if code not in confirmed_codes]
                )
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    (
                        f"Nothing saved. Unconfirmed stock codes detected. "
                        f"Got {uncomfirmed_codes}. "
                    ),
                )
                url = reverse(
                    "edc_pharmacy:allocate_url",
                    kwargs={
                        "stock_request": stock_request.id,
                        "assignment": assignment.id,
                    },
                )
                return url
        return None

    def redirect_on_invalid_stock_codes(
        self, stock_codes: list[str], stock_request: StockRequest, assignment: Assignment
    ) -> str | None:
        if stock_codes and Stock.objects.filter(code__in=stock_codes).count() != len(
            stock_codes
        ):
            valid_codes = Stock.objects.filter(code__in=stock_codes).values_list(
                "code", flat=True
            )
            invalid_codes = " ,".join(
                [code for code in stock_codes if code not in valid_codes]
            )
            messages.add_message(
                self.request,
                messages.ERROR,
                f"Nothing saved. Invalid codes detected. Got {invalid_codes}. ",
            )
            url = reverse(
                "edc_pharmacy:allocate_url",
                kwargs={
                    "stock_request": stock_request.id,
                    "assignment": assignment.id,
                },
            )
            return url
        return None

    def redirect_on_has_multiple_container_types(
        self, stock_codes: list[str], stock_request: StockRequest, assignment: Assignment
    ) -> str | None:
        if stock_codes and Stock.objects.filter(
            code__in=stock_codes, container=stock_request.container
        ).count() != len(stock_codes):
            messages.add_message(
                self.request,
                messages.ERROR,
                (
                    f"Nothing saved. Container mismatch for request. "
                    f"Expected `{stock_request.container}` "
                    f"only. See Stock request {stock_request.request_identifier} "
                ),
            )
            url = reverse(
                "edc_pharmacy:allocate_url",
                kwargs={
                    "stock_request": stock_request.id,
                    "assignment": assignment.id,
                },
            )
            return url
        return None

    def redirect_on_stock_already_allocated(
        self, stock_codes: list[str], stock_request: StockRequest, assignment: Assignment
    ) -> str | None:
        if (
            stock_codes
            and Stock.objects.filter(code__in=stock_codes, allocation__isnull=False).exists()
        ):
            allocated_stock_codes = []
            for stock in Stock.objects.filter(code__in=stock_codes):
                if stock.allocation:
                    allocated_stock_codes.append(stock.code)
            messages.add_message(
                self.request,
                messages.ERROR,
                f"Stock already allocated. Got {','.join(allocated_stock_codes)}.",
            )
            url = reverse(
                "edc_pharmacy:allocate_url",
                kwargs={
                    "stock_request": stock_request.id,
                    "assignment": getattr(assignment, "id", None),
                },
            )
            return url
        return None

    def redirect_on_all_allocated_for_assignment(
        self, stock_request: StockRequest, assignment: Assignment
    ) -> str | None:

        if not stock_request.stockrequestitem_set.filter(
            allocation__isnull=True, assignment=assignment
        ).exists():
            messages.add_message(
                self.request,
                messages.INFO,
                _(
                    "All subjects in this stock request assigned '%(assignment)s' "
                    "medication have been allocated stock"
                )
                % {"assignment": assignment.display_name.upper()},
            )
            url = reverse(
                "edc_pharmacy:allocate_url",
                kwargs={
                    "stock_request": stock_request.id,
                    "assignment": getattr(assignment, "id", None),
                },
            )
            return url
        return None

    def redirect_on_incorrect_stock_for_assignment(
        self, stock_codes: list[str], stock_request: StockRequest, assignment: Assignment
    ) -> str | None:

        if stock_codes and Stock.objects.filter(
            code__in=stock_codes, lot__assignment=assignment
        ).count() != len(stock_codes):
            messages.add_message(
                self.request,
                messages.ERROR,
                (
                    "One or more stock codes are not for this assignment. "
                    f"Expected `{assignment.display_name}` only. Check your work."
                ),
            )
            url = reverse(
                "edc_pharmacy:allocate_url",
                kwargs={
                    "stock_request": stock_request.id,
                    "assignment": getattr(assignment, "id", None),
                },
            )
            return url
        return None

    def get_counts(self, stock_request: StockRequest) -> tuple[int, int]:
        if self.selected_assignment:
            total_count = stock_request.stockrequestitem_set.all().count()
            groupby = (
                stock_request.stockrequestitem_set.values("assignment__name")
                .filter(allocation__isnull=True, allocation__stock__isnull=True)
                .annotate(count=Count("assignment__name"))
            )
            groupby = {dct["assignment__name"]: dct["count"] for dct in groupby}
            remaining_count = groupby.get(self.selected_assignment.name)
            return remaining_count or 0, total_count
        return 0, 0

    def post(self, request, *args, **kwargs):
        stock_codes = request.POST.getlist("codes") if request.POST.get("codes") else None
        subject_identifiers = request.POST.get("subject_identifiers")
        assignment_id = request.POST.get("assignment")
        subject_identifiers = ast.literal_eval(subject_identifiers)
        stock_request = StockRequest.objects.get(id=kwargs.get("stock_request"))
        assignment = self.get_assignment(assignment_id)

        if url := self.redirect_on_all_allocated_for_assignment(stock_request, assignment):
            return HttpResponseRedirect(url)
        if url := self.redirect_on_has_duplicates(stock_codes, stock_request, assignment):
            return HttpResponseRedirect(url)
        if url := self.redirect_on_invalid_stock_codes(stock_codes, stock_request, assignment):
            return HttpResponseRedirect(url)
        if url := self.redirect_on_uncomfirmed_stock_codes(
            stock_codes, stock_request, assignment
        ):
            return HttpResponseRedirect(url)
        if url := self.redirect_on_has_multiple_container_types(
            stock_codes, stock_request, assignment
        ):
            return HttpResponseRedirect(url)
        if url := self.redirect_on_incorrect_stock_for_assignment(
            stock_codes, stock_request, assignment
        ):
            return HttpResponseRedirect(url)

        if stock_codes and subject_identifiers and assignment:
            allocation_data = dict(zip(stock_codes, subject_identifiers))
            try:
                allocated, not_allocated = allocate_stock(
                    stock_request,
                    allocation_data,
                    allocated_by=request.user.username,
                    user_created=request.user.username,
                    created=get_utcnow(),
                )
            except AllocationError as e:
                messages.add_message(request, messages.ERROR, str(e))
            except InsufficientStockError as e:
                messages.add_message(request, messages.ERROR, str(e))
            else:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Allocated {len(allocated)} stock records. "
                    f"Skipped {len(not_allocated)}. Skipped {', '.join(not_allocated)}",
                )
            if self.get_next_subject_identifiers():
                url = reverse(
                    "edc_pharmacy:allocate_url",
                    kwargs={
                        "stock_request": stock_request.id,
                        "assignment": assignment.id,
                    },
                )
                return HttpResponseRedirect(url)
            return HttpResponseRedirect(self.stock_request_changelist_url)
        url = reverse(
            "edc_pharmacy:allocate_url",
            kwargs={
                "stock_request": stock_request.id,
                "assignment": getattr(assignment, "id", None),
            },
        )
        return HttpResponseRedirect(url)
