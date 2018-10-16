from django.conf import settings
from django.contrib import admin
from django.contrib.admin.options import TabularInline
from django.urls.base import reverse
from django.utils.safestring import mark_safe
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
                'instructions',
            )}),
        ('Reference Information', {
            'classes': ('collapse', ),
            'fields': (
                'related_action_item',
                'parent_action_item',
                'auto_created',
                'auto_created_comment',
            )}),
        ('Email', {
            'classes': ('collapse', ),
            'fields': (
                'emailed',
                'emailed_datetime',
            )}),
        audit_fieldset_tuple
    )

    radio_fields = {'status': admin.VERTICAL}

    inlines = [ActionItemUpdateInline]

    list_display = ('identifier', 'dashboard',
                    'action_type', 'priority', 'status', 'emailed', 'parent_action',
                    'related_action_item', 'created')

    list_filter = ('status', 'priority', 'emailed',
                   'report_datetime', 'action_type__name')

    search_fields = ('subject_identifier',
                     'action_identifier',
                     'related_action_item__action_identifier',
                     'parent_action_item__action_identifier',
                     'action_type__name',
                     'action_type__display_name',
                     'id')

    ordering = ('action_type__display_name', )

    date_hierarchy = 'created'

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = fields + ('action_identifier', 'instructions',
                           'auto_created', 'auto_created_comment',
                           'reference_model', 'emailed', 'emailed_datetime',
                           'related_action_item',
                           'parent_action_item',
                           )
        if obj:
            fields = fields + ('subject_identifier',
                               'report_datetime',
                               'action_type')
        return fields

    def parent_action(self, obj):
        """Returns a url to the parent action item
        for display in admin.
        """
        if obj.parent_action_item:
            url_name = '_'.join(obj._meta.label_lower.split('.'))
            namespace = edc_action_item_admin.name
            url = reverse(
                f'{namespace}:{url_name}_changelist')
            return mark_safe(
                f'<a data-toggle="tooltip" title="go to parent action item" '
                f'href="{url}?q={obj.parent_action_item.action_identifier}">'
                f'{obj.parent_action_item.identifier}</a>')
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'action_type':
            kwargs["queryset"] = db_field.related_model.objects.filter(
                create_by_user=True)
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs)

    def post_url_on_delete_kwargs(self, request, obj):
        return dict(subject_identifier=obj.subject_identifier)
