from django.contrib import admin
from django.template.loader import render_to_string
from django_audit_fields.admin import audit_fieldset_tuple
from edc_consent.utils import get_consent_model_cls
from edc_constants.constants import NO, YES
from edc_model_admin.mixins import ModelAdminProtectPiiMixin
from edc_utils import age, get_utcnow

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
        "subject",
        "dashboard",
        "contacts",
        "contact_rules",
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

    @admin.display(description="Subject", ordering="subject_identifier")
    def subject(self, obj):
        consent = get_consent_model_cls().objects.get(
            subject_identifier=obj.subject_identifier
        )
        context = dict(
            subject_identifier=obj.subject_identifier,
            gender=consent.gender.upper(),
            age_in_years=age(born=consent.dob, reference_dt=get_utcnow()).years,
            initials=consent.initials,
        )
        return render_to_string("changelist_locator_subject.html", context=context)

    @admin.display(description="Contact Rules", ordering="may_call")
    def contact_rules(self, obj):
        context = dict(
            may_visit_home=obj.may_visit_home,
            may_call=obj.may_call,
            sms=obj.sms,
            call_work=obj.call_work,
            contact_indirectly=obj.contact_indirectly,
            YES=YES,
            NO=NO,
        )
        return render_to_string("changelist_locator_contact_rules.html", context=context)

    @admin.display(description="Contacts")
    def contacts(self, obj):
        context = dict(
            subject_cell=obj.subject_cell,
            subject_cell_alt=obj.subject_cell_alt,
            subject_phone=obj.subject_phone,
            subject_phone_alt=obj.subject_phone_alt,
        )
        return render_to_string("changelist_locator_contacts.html", context=context)
