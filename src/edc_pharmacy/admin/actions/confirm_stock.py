from __future__ import annotations

from uuid import uuid4

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext

from ...models import Receive, RepackRequest, Stock


@admin.display(description="Confirm repacked and labeled stock")
def confirm_repacked_stock_action(modeladmin, request, queryset: QuerySet[RepackRequest]):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        return confirm_stock_from_queryset(modeladmin, request, queryset)
    return None


@admin.display(description="Confirm received and labeled stock")
def confirm_received_stock_action(modeladmin, request, queryset: QuerySet[RepackRequest]):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        return confirm_stock_from_queryset(modeladmin, request, queryset)
    return None


@admin.display(description="Confirm labeled stock")
def confirm_stock_from_queryset(
    modeladmin, request, queryset: QuerySet[RepackRequest | Receive | Stock]
):
    stock_codes = []
    pk = None
    identifier = None
    model_name = None
    word = "confirmed"
    if queryset.count() == 1:
        if queryset.model == RepackRequest:
            stock_qs = Stock.objects.filter(
                repack_request__pk__in=[obj.pk for obj in queryset]
            )
            stock_codes = stock_qs.values_list("code", flat=True)
            pk = queryset.first().pk
            identifier = queryset.first().repack_identifier
            model_name = queryset.model._meta.verbose_name
        elif queryset.model == Receive:
            stock_qs = Stock.objects.filter(
                receive_item__receive__pk__in=[obj.pk for obj in queryset]
            )
            stock_codes = stock_qs.values_list("code", flat=True)
            pk = queryset.first().pk
            identifier = queryset.first().receive_identifier
            model_name = queryset.model._meta.verbose_name
    elif queryset.count() > 1:
        stock_codes = queryset.values_list("code", flat=True)

    if queryset.count() >= 1:
        session_uuid = str(uuid4())
        request.session[session_uuid] = {
            "stock_codes": [str(o) for o in stock_codes],
            "source_pk": pk,
            "source_identifier": identifier,
            "source_label_lower": queryset.model._meta.label_lower,
            "source_model_name": model_name,
            "transaction_word": word,
        }
        url = reverse(
            "edc_pharmacy:confirm_stock_from_queryset_url",
            kwargs={"session_uuid": session_uuid},
        )
        return HttpResponseRedirect(url)
    return None
