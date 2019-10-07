from ..get_ae_model import get_ae_model


class NonAeInitialModelAdminMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ae_initial":
            if request.GET.get("ae_initial"):
                kwargs["queryset"] = get_ae_model("aeinitial").objects.filter(
                    id__exact=request.GET.get("ae_initial", 0)
                )
            else:
                kwargs["queryset"] = get_ae_model("aeinitial").objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        if obj:
            fields = list(fields) + ["ae_initial"]
        return list(fields)
