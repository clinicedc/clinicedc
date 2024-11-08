from ...views import IntermediateView


def update_label_configuration_action(modeladmin, request, queryset):
    return IntermediateView(request=request, model_pks=[o.id for o in queryset]).get(request)
