from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from ..models import StorageBin, StorageBinItem


@login_required
def print_bin_labels_view(request, storage_bin):
    bin_obj = get_object_or_404(StorageBin, pk=storage_bin)
    stock_pks = list(
        StorageBinItem.objects.filter(storage_bin=bin_obj).values_list(
            "stock_id", flat=True
        )
    )
    session_uuid = str(uuid4())
    request.session[session_uuid] = [str(pk) for pk in stock_pks]
    return HttpResponseRedirect(
        reverse(
            "edc_pharmacy:print_labels_url",
            kwargs={"session_uuid": session_uuid, "model": "stock"},
        )
    )
