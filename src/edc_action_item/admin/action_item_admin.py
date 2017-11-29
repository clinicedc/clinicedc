from django.contrib import admin
from django.contrib.admin.options import TabularInline
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.inlines import TabularInlineMixin

from ..admin_site import edc_action_item_admin
from ..forms import ActionItemForm
from ..models import ActionItem
from ..models import ActionItemUpdate
from .modeladmin_mixins import ModelAdminMixin


class ActionItemUpdateInline(TabularInlineMixin, TabularInline):
    model = ActionItemUpdate
    extra = 0
    min_num = 1
    fields = (
        'comment',
        'follow_up',
        'closed',
        'report_datetime')

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        return fields + ('report_datetime',)


@admin.register(ActionItem, site=edc_action_item_admin)
class ActionItemAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = ActionItemForm

    fieldsets = (
        (None, {
            'fields': (
                'action_identifier',
                'subject_identifier',
                'report_datetime',
                'title',
                'status',
                'comment',
                'auto_created',
                'auto_created_comment'
            )},
         ),
        audit_fieldset_tuple
    )

    radio_fields = {'status': admin.VERTICAL}

    inlines = [ActionItemUpdateInline]

    list_display = ('action_identifier', 'dashboard', 'title', 'status')

    list_filter = ('status', 'report_datetime')

    search_fields = ('subject_identifier', 'action_identifier')

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = fields + ('action_identifier',
                           'auto_created', 'auto_created_comment')
        if obj:
            fields = fields + ('subject_identifier', 'report_datetime')
        return fields
