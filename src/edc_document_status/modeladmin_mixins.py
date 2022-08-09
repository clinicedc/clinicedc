from typing import Tuple


class DocumentStatusModelAdminMixin:
    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return tuple(set(readonly_fields + ("document_status",)))
