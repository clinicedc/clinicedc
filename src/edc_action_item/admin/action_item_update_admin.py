from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_action_item_admin
from ..forms import ActionItemUpdateForm
from ..models import ActionItemUpdate
from .modeladmin_mixins import ModelAdminMixin


@admin.register(ActionItemUpdate, site=edc_action_item_admin)
class ActionItemUpdateAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = ActionItemUpdateForm

    fieldsets = (
        (None, {
            'fields': (
                'action_item',
                'report_datetime',
                'comment',
            )},
         ),
        audit_fieldset_tuple
    )

    list_display = ('subject_identifier',
                    'action_identifier', 'report_datetime')

    list_filter = ('report_datetime', )

    search_fields = ('action_item__subject_identifier',
                     'action_item__action_identifier',
                     'comment')
