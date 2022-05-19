class DocumentStatusModelAdminMixin:
    def get_readonly_fields(self, request, obj=None) -> list:
        readonly_fields = super().get_readonly_fields(request, obj=obj)  # type: ignore
        if "document_status" not in readonly_fields:
            return list(readonly_fields) + ["document_status"]
        return list(readonly_fields)
