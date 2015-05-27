from lis.core.lab_reference.models import BaseReferenceListItem


def toggle_active(modeladmin, request, queryset):
        for qs in queryset:
            if not isinstance(qs, BaseReferenceListItem):
                modeladmin.message_user(request, 'Records must be a list item. (BaseReferenceListItem)')
                break
            else:
                qs.active = not qs.active
                qs.save()
toggle_active.short_description = "toggle active/inactive"


def toggle_scale(modeladmin, request, queryset):
        for qs in queryset:
            if not isinstance(qs, BaseReferenceListItem):
                modeladmin.message_user(request, 'Records must be a list item. (BaseReferenceListItem)')
                break
            else:
                qs.scale = 'increasing' if  qs.scale == 'decreasing' else 'decreasing'
                qs.save()
toggle_scale.short_description = "toggle scale increasing/decreasing"


def toggle_lln(modeladmin, request, queryset):
        for qs in queryset:
            if not isinstance(qs, BaseReferenceListItem):
                modeladmin.message_user(request, 'Records must be a list item. (BaseReferenceListItem)')
                break
            else:
                qs.use_lln = not qs.use_lln
                qs.save()
toggle_lln.short_description = "toggle LLN"


def toggle_uln(modeladmin, request, queryset):
        for qs in queryset:
            if not isinstance(qs, BaseReferenceListItem):
                modeladmin.message_user(request, 'Records must be a list item. (BaseReferenceListItem)')
                break
            else:
                qs.use_uln = not qs.use_uln
                qs.save()
toggle_uln.short_description = "toggle ULN"


def toggle_serum(modeladmin, request, queryset):
        for qs in queryset:
            if not isinstance(qs, BaseReferenceListItem):
                modeladmin.message_user(request, 'Records must be a list item. (BaseReferenceListItem)')
                break
            else:
                if qs.serum == 'LOW':
                    qs.serum = 'HIGH'
                if qs.serum == 'HIGH':
                    qs.serum = 'N/A'
                if qs.serum == 'N/A':
                    qs.serum = 'LOW'
                qs.save()
toggle_uln.short_description = "toggle Serum (low->high->N/A)"
