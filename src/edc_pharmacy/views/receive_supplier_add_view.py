"""View for quickly adding a Supplier from the order edit page.

Supports both AJAX (Bootstrap modal) and non-AJAX (popup fallback) POST.
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ..forms.stock import SupplierAddForm


@method_decorator(login_required, name="dispatch")
class ReceiveSupplierAddView(TemplateView):
    """Handles both popup (legacy) and AJAX modal submissions.

    - AJAX POST  → returns JSON ``{"pk": "...", "name": "..."}`` on success,
                   or ``{"errors": {...}}`` on validation failure (HTTP 400).
    - Normal POST → renders the template closer page (popup fallback).
    - GET        → renders the standalone popup page (popup fallback).
    """

    template_name = "edc_pharmacy/stock/supplier_add_popup.html"

    def _is_ajax(self, request):
        return request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def get_context_data(self, form=None, **kwargs):
        return super().get_context_data(form=form or SupplierAddForm(), **kwargs)

    def post(self, request, *args, **kwargs):
        form = SupplierAddForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user_created = request.user.username
            obj.user_modified = request.user.username
            obj.save()
            if self._is_ajax(request):
                return JsonResponse({"pk": str(obj.pk), "name": str(obj)})
            # Non-AJAX popup: render closer page
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    saved_pk=str(obj.pk),
                    saved_name=str(obj),
                )
            )
        if self._is_ajax(request):
            return JsonResponse({"errors": form.errors}, status=400)
        return self.render_to_response(self.get_context_data(form=form))
