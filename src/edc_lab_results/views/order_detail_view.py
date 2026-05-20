from __future__ import annotations

from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..forms import OrderUpdateForm
from ..models import Result


class OrderDetailView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_lab_results/order_detail.html"
    navbar_selected_item = "edc_lab_results"

    def get_results(self, order_no: str) -> Result:
        results = Result.objects.filter(order_no=order_no).order_by("investigation")
        if not results.exists():
            raise Http404(f"No results for order {order_no}")
        return results

    def get_header(self, first: Result) -> dict:
        return {
            "subject_identifier": first.subject_identifier,
            "screening_identifier": first.screening_identifier,
            "age": first.age,
            "sex": first.sex,
            "visit_code": first.visit_code,
            "visit_code_sequence": first.visit_code_sequence,
            "order_no": first.order_no,
            "order_datetime": first.order_datetime,
            "sample_no": first.sample_no,
            "result_no": first.result_no,
            "specimen_collected_datetime": first.specimen_collected_datetime,
            "name_id": first.name_id,
            "source_file": first.source_file,
        }

    @staticmethod
    def _initial_visit_value(first: Result) -> str:
        if first.visit_code:
            seq = first.visit_code_sequence or 0
            return f"{first.visit_code}.{seq}"
        return ""

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        order_no = self.kwargs["order_no"]
        results = self.get_results(order_no)
        first = results.first()
        header = self.get_header(first)

        if "form" not in kwargs:
            form = OrderUpdateForm(
                order_datetime=first.order_datetime,
                initial={
                    "subject_identifier": first.subject_identifier,
                    "screening_identifier": first.screening_identifier,
                    "visit": self._initial_visit_value(first),
                },
            )
        else:
            form = kwargs["form"]

        context.update(
            header=header,
            results=results,
            form=form,
            initial_visit=self._initial_visit_value(first),
        )
        return context

    def post(self, request: object, *args: object, **kwargs: object) -> object:  # noqa: ARG002
        order_no = self.kwargs["order_no"]
        order_datetime = (
            Result.objects.filter(order_no=order_no)
            .values_list("order_datetime", flat=True)
            .first()
        )
        form = OrderUpdateForm(request.POST, order_datetime=order_datetime)
        if form.is_valid():
            subject_identifier = form.cleaned_data["subject_identifier"]
            screening_identifier = form.cleaned_data["screening_identifier"] or ""

            update_fields: dict = {"screening_identifier": screening_identifier}
            if subject_identifier:
                update_fields["subject_identifier"] = subject_identifier
                update_fields["subject_not_found"] = False
                update_fields["visit_code"] = form.cleaned_data["visit_code"]
                update_fields["visit_code_sequence"] = form.cleaned_data[
                    "visit_code_sequence"
                ]

            updated = Result.objects.filter(order_no=order_no).update(**update_fields)
            messages.success(
                request,
                f"Updated {updated} result(s) for order {order_no}.",
            )
            return HttpResponseRedirect(
                reverse("edc_lab_results:order-detail", kwargs={"order_no": order_no})
            )
        return self.render_to_response(self.get_context_data(form=form))
