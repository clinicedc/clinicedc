"""View for editing an existing Supplier from the order edit page.

GET  → returns JSON {pk, name, contact, telephone, email} for pre-populating
       the edit modal.
POST → validates, saves, returns JSON {pk, name} on success or
       {errors: {...}} on failure (HTTP 400).
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View

from ..forms.stock import SupplierAddForm
from ..models import Supplier


@method_decorator(login_required, name="dispatch")
class ReceiveSupplierEditView(View):
    def get(self, request, pk, *args, **kwargs):  # noqa: ARG002
        supplier = get_object_or_404(Supplier, pk=pk)
        return JsonResponse(
            {
                "pk": str(supplier.pk),
                "name": supplier.name,
                "contact": supplier.contact or "",
                "telephone": supplier.telephone or "",
                "email": supplier.email or "",
                "address_one": supplier.address_one or "",
                "address_two": supplier.address_two or "",
                "city": supplier.city or "",
                "state": supplier.state or "",
                "postal_code": supplier.postal_code or "",
                "country": supplier.country or "",
            }
        )

    def post(self, request, pk, *args, **kwargs):  # noqa: ARG002
        supplier = get_object_or_404(Supplier, pk=pk)
        form = SupplierAddForm(request.POST, instance=supplier)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user_modified = request.user.username
            obj.save()
            return JsonResponse({"pk": str(obj.pk), "name": str(obj)})
        return JsonResponse({"errors": form.errors}, status=400)
