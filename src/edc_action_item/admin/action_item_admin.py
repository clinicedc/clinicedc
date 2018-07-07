from django.conf import settings
from django.contrib import admin
from django.contrib.admin.options import TabularInline
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.inlines import TabularInlineMixin
from edc_subject_dashboard import ModelAdminSubjectDashboardMixin

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
        'report_datetime')

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        return fields + ('report_datetime',)


@admin.register(ActionItem, site=edc_action_item_admin)
class ActionItemAdmin(ModelAdminMixin, ModelAdminSubjectDashboardMixin, admin.ModelAdmin):

    form = ActionItemForm

    save_on_top = True

    subject_dashboard_url = 'subject_dashboard_url'

    post_url_on_delete_name = settings.DASHBOARD_URL_NAMES.get(
        subject_dashboard_url)

    fieldsets = (
        (None, {
            'fields': (
                'action_identifier',
                'subject_identifier',
                'report_datetime',
                'action_type',
                'priority',
                'status',
                'parent_action_item',
                'instructions',
            )}),
        ('Reference Information', {
            'classes': ('collapse', ),
            'fields': (
                'reference_model',
                'related_reference_identifier',
                'parent_reference_identifier',
                'auto_created',
                'auto_created_comment',
            )}),
        audit_fieldset_tuple
    )

    radio_fields = {'status': admin.VERTICAL}

    inlines = [ActionItemUpdateInline]

    list_display = ('identifier', 'dashboard',
                    'action_type', 'priority', 'status', 'parent',
                    'reference', 'related_reference', 'parent_reference')

    list_filter = ('status', 'priority',
                   'report_datetime', 'action_type__name')

    search_fields = ('subject_identifier',
                     'action_identifier',
                     'related_reference_identifier',
                     'parent_reference_identifier',
                     'action_type__name',
                     'action_type__display_name',
                     'parent_action_item__action_identifier')

    ordering = ('action_type__display_name', )

    date_hierarchy = 'created'

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = fields + ('action_identifier', 'instructions',
                           'auto_created', 'auto_created_comment',
                           'reference_model',
                           'related_reference_identifier',
                           'parent_reference_identifier',
                           'parent_action_item',
                           )
        if obj:
            fields = fields + ('subject_identifier',
                               'report_datetime',
                               'action_type')
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'action_type':
            kwargs["queryset"] = db_field.related_model.objects.filter(
                create_by_user=True)
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs)

    def post_url_on_delete_kwargs(self, request, obj):
        return dict(subject_identifier=obj.subject_identifier)
