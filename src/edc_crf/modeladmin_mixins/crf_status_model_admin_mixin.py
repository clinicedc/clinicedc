from __future__ import annotations


class CrfStatusModelAdminMixin:
    def get_list_display(self, request) -> tuple[str, ...]:
        list_display = super().get_list_display(request)
        if "crf_status" not in list_display:
            list_display = list_display + ("crf_status",)
        return list_display

    def get_list_filter(self, request) -> tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        if "crf_status" not in list_filter:
            list_filter = ("crf_status",) + list_filter
        return list_filter
