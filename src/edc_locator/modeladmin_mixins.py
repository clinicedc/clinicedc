from django.contrib import admin
from django.template.loader import render_to_string
from django_audit_fields.admin import audit_fieldset_tuple
from edc_constants.constants import NO, YES
from edc_model_admin.mixins import ModelAdminProtectPiiMixin

from .fieldsets import (
    indirect_contacts_fieldset,
    subject_contacts_fieldset,
    work_contacts_fieldset,
)
from .forms import SubjectLocatorForm


class SubjectLocatorModelAdminMixin(ModelAdminProtectPiiMixin):
    form = SubjectLocatorForm

    extra_pii_attrs: list[str] = ["contacts"]

    fieldsets = (
        (None, {"fields": ("subject_identifier",)}),
        subject_contacts_fieldset,
        work_contacts_fieldset,
        indirect_contacts_fieldset,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "may_visit_home": admin.VERTICAL,
        "may_call": admin.VERTICAL,
        "may_sms": admin.VERTICAL,
        "may_call_work": admin.VERTICAL,
        "may_contact_indirectly": admin.VERTICAL,
    }

    list_filter = (
        "may_visit_home",
        "may_call",
        "may_sms",
        "may_call_work",
        "may_contact_indirectly",
    )

    list_display = (
        "subject_identifier",
        "dashboard",
        "visit_home",
        "contacts",
        "call",
        "sms",
        "call_work",
        "contact_indirectly",
    )

    search_fields = (
        "subject_identifier",
        "subject_cell__exact",
        "subject_cell_alt__exact",
        "subject_phone__exact",
        "subject_phone_alt__exact",
        "subject_work_phone__exact",
        "subject_work_cell__exact",
        "indirect_contact_cell__exact",
        "indirect_contact_cell_alt__exact",
        "indirect_contact_phone__exact",
    )

    @admin.display(description="Call", ordering="may_call")
    def call(self, obj):
        context = dict(response=obj.may_call, YES=YES, NO=NO)
        return render_to_string("yes_no_coloring.html", context=context)

    @admin.display(description="SMS", ordering="sms")
    def sms(self, obj):
        context = dict(response=obj.sms, YES=YES, NO=NO)
        return render_to_string("yes_no_coloring.html", context=context)

    @admin.display(description="Call work", ordering="call_work")
    def call_work(self, obj):
        context = dict(response=obj.call_work, YES=YES, NO=NO)
        return render_to_string("yes_no_coloring.html", context=context)

    @admin.display(description="Contact indirectly", ordering="contact_indirectly")
    def contact_indirectly(self, obj):
        context = dict(response=obj.contact_indirectly, YES=YES, NO=NO)
        return render_to_string("yes_no_coloring.html", context=context)

    @admin.display(description="Contacts")
    def contacts(self, obj):
        context = dict(
            subject_cell=obj.subject_cell,
            subject_cell_alt=obj.subject_cell_alt,
            subject_phone=obj.subject_phone,
            subject_phone_alt=obj.subject_phone_alt,
        )
        return render_to_string("changelist_locator_contacts.html", context=context)
