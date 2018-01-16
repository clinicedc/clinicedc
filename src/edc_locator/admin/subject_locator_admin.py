from django.contrib import admin
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_locator_admin
from ..fieldsets import subject_contacts_fieldset
from ..fieldsets import indirect_contacts_fieldset, work_contacts_fieldset
from ..forms import SubjectLocatorForm
from ..models import SubjectLocator
from .modeladmin_mixins import ModelAdminMixin


@admin.register(SubjectLocator, site=edc_locator_admin)
class SubjectLocatorAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = SubjectLocatorForm

    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
            )}),
        subject_contacts_fieldset,
        work_contacts_fieldset,
        indirect_contacts_fieldset,
        audit_fieldset_tuple,
    )

    radio_fields = {
        'may_visit_home': admin.VERTICAL,
        'may_call': admin.VERTICAL,
        'may_sms': admin.VERTICAL,
        'may_call_work': admin.VERTICAL,
        'may_contact_indirectly': admin.VERTICAL}

    list_filter = (
        'may_visit_home',
        'may_call',
        'may_sms',
        'may_call_work',
        'may_contact_indirectly')

    list_display = (
        'subject_identifier',
        'dashboard',
        'visit_home',
        'call',
        'sms',
        'call_work',
        'contact_indirectly')

    search_fields = ('subject_identifier', )
