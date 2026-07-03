from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import QuerySet
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.views.generic import TemplateView

from edc_appointment.utils import get_appointment_model_cls
from edc_dashboard.url_names import url_names
from edc_dashboard.view_mixins import EdcViewMixin
from edc_lab.utils import get_requisition_model
from edc_navbar import NavbarViewMixin

from ..constants import LINKED
from ..forms import OrderUpdateForm
from ..import_results import LabResultImporter
from ..models import Result


class OrderDetailView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = "edc_lab_results/order_detail.html"
    navbar_selected_item = "edc_lab_results"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        order_no = self.kwargs["order_no"]
        results = self.get_results(order_no)
        result_obj = results.first()
        header_data = self.get_header_data(result_obj)
        visit = (
            f"{result_obj.visit_code}.{result_obj.visit_code_sequence or 0}"
            if result_obj.visit_code
            else ""
        )
        form = self.get_form(result_obj, visit, kwargs)

        next_url = self._safe_next()
        context.update(
            header=header_data,
            results=results,
            form=form,
            initial_visit=visit,
            dashboard_url=self.get_subject_dashboard_url(result_obj),
            candidate_requisitions=self._candidate_requisitions(results),
            back_url=self._back_url(result_obj, next_url),
            next_url=next_url,
        )
        return context

    def post(self, request: object, *args: object, **kwargs: object) -> object:  # noqa: ARG002
        if request.POST.get("selected_requisition"):
            return self.match_with_requisition_on_post(request)
        return self.update_order_on_post(request)

    @staticmethod
    def get_form(obj: Result, visit: str, kwargs: dict):
        if "form" not in kwargs:
            form = OrderUpdateForm(
                order_datetime=obj.order_datetime,
                initial={
                    "subject_identifier": obj.subject_identifier,
                    "screening_identifier": obj.screening_identifier,
                    "visit": visit,
                },
            )
        else:
            form = kwargs["form"]
        return form

    def get_results(self, order_no: str) -> QuerySet[Result]:
        results = Result.objects.filter(order_no=order_no).order_by("investigation")
        if not results.exists():
            raise Http404(f"No results for order {order_no}")
        return results

    def get_header_data(self, obj: Result) -> dict:
        return {
            "subject_identifier": obj.subject_identifier,
            "screening_identifier": obj.screening_identifier,
            "age": obj.age,
            "sex": obj.sex,
            "visit_code": obj.visit_code,
            "visit_code_sequence": obj.visit_code_sequence,
            "order_no": obj.order_no,
            "order_datetime": obj.order_datetime,
            "sample_no": obj.sample_no,
            "result_no": obj.result_no,
            "specimen_collected_datetime": obj.specimen_collected_datetime,
            "name_id": obj.name_id,
            "source_file": obj.source_file,
        }

    def _safe_next(self) -> str:
        """Return the ``next`` param (from POST or GET) if it is a safe
        local URL, else empty string.
        """
        nxt = self.request.POST.get("next") or self.request.GET.get("next") or ""
        if nxt and url_has_allowed_host_and_scheme(
            nxt, allowed_hosts={self.request.get_host()}
        ):
            return nxt
        return ""

    def _back_url(self, obj: Result, next_url: str) -> str:
        """Where the Back button goes: the referring page if provided,
        otherwise the subject/order lookup filtered to this order.
        """
        if next_url:
            return next_url
        identifier = obj.subject_identifier or obj.screening_identifier or ""
        return f"{reverse('edc_lab_results:subject-results')}?identifier={identifier}"

    @staticmethod
    def _candidate_requisitions(results) -> list[dict]:
        """For an order with ambiguous results, resolve the union of their
        requisition_candidates into displayable requisition options."""
        candidate_ids = sorted(
            {
                cid
                for result in results
                if result.requisition_ambiguous
                for cid in (result.requisition_candidates or [])
            }
        )
        if not candidate_ids:
            return []
        reqs = {
            req.requisition_identifier: req
            for req in get_requisition_model()
            .objects.filter(requisition_identifier__in=candidate_ids)
            .select_related("panel", "subject_visit")
        }
        options: list[dict] = []
        for cid in candidate_ids:
            req = reqs.get(cid)
            options.append(
                {
                    "requisition_identifier": cid,
                    "panel": (req.panel.name if req and req.panel else ""),
                    "drawn_datetime": (req.drawn_datetime if req else None),
                    "visit": (f"{req.visit_code}.{req.visit_code_sequence}" if req else ""),
                }
            )
        return options

    @staticmethod
    def get_subject_dashboard_url(obj: Result) -> str:
        """Return the subject dashboard URL for this result's
        appointment, or empty string if not enough data to resolve.
        """
        if not obj.subject_identifier:
            return ""
        dashboard_url_name = url_names.get("subject_dashboard_url")
        opts = {"subject_identifier": obj.subject_identifier}
        try:
            appointment = (
                get_appointment_model_cls()
                .objects.values("pk")
                .get(
                    subject_identifier=obj.subject_identifier,
                    visit_code=obj.visit_code,
                    visit_code_sequence=obj.visit_code_sequence or 0,
                )
            )
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            pass
        else:
            opts.update(appointment=str(appointment.get("pk")))
        return reverse(dashboard_url_name, kwargs=opts)

    def match_with_requisition_on_post(self, request: object) -> object:
        """Link the order's ambiguous results to the reviewer's
        selected requisition (only those whose candidates include
        it).
        """
        order_no = self.kwargs["order_no"]
        requisition_identifier = request.POST.get("selected_requisition", "").strip()
        try:
            requisition_obj = (
                get_requisition_model()
                .objects.select_related("subject_visit")
                .get(requisition_identifier=requisition_identifier)
            )
        except ObjectDoesNotExist:
            messages.error(request, f"Requisition {requisition_identifier} not found.")
            return self.redirect_to_self(order_no)

        pks = [
            result.pk
            for result in Result.objects.filter(order_no=order_no, requisition_ambiguous=True)
            if requisition_identifier in (result.requisition_candidates or [])
        ]
        updated = Result.objects.filter(pk__in=pks).update(
            requisition_identifier=requisition_identifier,
            visit_code=requisition_obj.visit_code,
            visit_code_sequence=requisition_obj.visit_code_sequence,
            requisition_ambiguous=False,
            requisition_match_category=LINKED,
            requisition_match_comment="",
            requisition_candidates=[],
        )
        messages.success(
            request,
            f"Linked {updated} result(s) to requisition {requisition_identifier}.",
        )
        return self.redirect_to_self(order_no)

    def update_order_on_post(self, request: object) -> object:
        order_no = self.kwargs["order_no"]
        order_datetime = (
            Result.objects.filter(order_no=order_no)
            .values_list("order_datetime", flat=True)
            .first()
        )
        form = OrderUpdateForm(request.POST, order_datetime=order_datetime)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        subject_identifier = form.cleaned_data["subject_identifier"]
        screening_identifier = form.cleaned_data["screening_identifier"] or ""
        visit_code = ""
        visit_code_sequence = None

        update_fields: dict = {"screening_identifier": screening_identifier}
        if subject_identifier:
            visit_code = form.cleaned_data["visit_code"]
            visit_code_sequence = form.cleaned_data["visit_code_sequence"]
            update_fields["subject_identifier"] = subject_identifier
            update_fields["subject_not_found"] = False
            update_fields["visit_code"] = visit_code
            update_fields["visit_code_sequence"] = visit_code_sequence

        updated = Result.objects.filter(order_no=order_no).update(**update_fields)
        msg = f"Updated {updated} result(s) for order {order_no}."
        if visit_code:
            linked = self.link_order_to_visit_requisitions(
                order_no, subject_identifier, visit_code, visit_code_sequence
            )
            if linked:
                msg += f" Linked {linked} to the requisition for visit {visit_code}."
        messages.success(request, msg)
        return self.redirect_to_self(order_no)

    @staticmethod
    def link_order_to_visit_requisitions(
        order_no: str,
        subject_identifier: str,
        visit_code: str,
        visit_code_sequence: int,
    ) -> int:
        """Link each result in the order to the requisition at the chosen
        visit whose panel reports the result's utest_id. Results whose
        requisition does not exist at that visit are left unlinked.
        """
        panel_index = LabResultImporter._build_utest_id_panel_index()
        requisitions = list(
            get_requisition_model()
            .objects.filter(
                subject_identifier=subject_identifier,
                subject_visit__visit_code=visit_code,
                subject_visit__visit_code_sequence=visit_code_sequence,
            )
            .select_related("panel")
        )
        linked = 0
        for result in Result.objects.filter(order_no=order_no):
            panel_names = panel_index.get(result.utest_id)
            if not panel_names:
                continue
            matches = [
                req
                for req in requisitions
                if req.panel and req.panel.name in panel_names
            ]
            if len(matches) == 1:
                Result.objects.filter(pk=result.pk).update(
                    requisition_identifier=matches[0].requisition_identifier,
                    requisition_ambiguous=False,
                    requisition_match_category=LINKED,
                    requisition_match_comment="",
                    requisition_candidates=[],
                )
                linked += 1
        return linked

    def redirect_to_self(self, order_no: str) -> HttpResponseRedirect:
        url = reverse("edc_lab_results:order-detail", kwargs={"order_no": order_no})
        next_url = self._safe_next()
        if next_url:
            url = f"{url}?{urlencode({'next': next_url})}"
        return HttpResponseRedirect(url)
