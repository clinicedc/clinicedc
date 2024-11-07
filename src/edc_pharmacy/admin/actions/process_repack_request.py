from __future__ import annotations

from ...utils import process_repack_request


def process_repack_request_action(modeladmin, request, queryset):
    for repackage_obj in queryset:
        for i in range(0, int(repackage_obj.qty)):
            process_repack_request(repackage_obj)
