from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_action_item_admin
from ..forms import ActionTypeForm
from ..models import ActionType
from .modeladmin_mixins import ModelAdminMixin


@admin.register(ActionType, site=edc_action_item_admin)
class ActionTypeAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = ActionTypeForm

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'display_name',
                'prn_form_action',
                'model',
                'show_on_dashboard',
                'instructions',
            )},
         ),
        audit_fieldset_tuple
    )

    radio_fields = {'prn_form_action': admin.VERTICAL}

    list_display = ('name', 'prn', 'model', 'show_on_dashboard')

    list_filter = ('prn_form_action', 'show_on_dashboard')

    search_fields = ('name', 'display_name', 'model')
