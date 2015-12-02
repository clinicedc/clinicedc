from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin


class BaseLocatorModelAdmin(BaseModelAdmin):

    fields = (
        'subject_consent',
        'date_signed',
        'mail_address',
        # 'care_clinic',
        'home_visit_permission',
        'physical_address',
        'may_follow_up',
        'subject_cell',
        'subject_cell_alt',
        'subject_phone',
        'subject_phone_alt',
        'may_call_work',
        'subject_work_place',
        'subject_work_phone',
        'may_contact_someone',
        'contact_name',
        'contact_rel',
        'contact_physical_address',
        'contact_cell',
        'contact_phone',
        'has_caretaker_alt',
        'caretaker_name',
        'caretaker_cell',
        'caretaker_tel',
    )

    radio_fields = {
        "home_visit_permission": admin.VERTICAL,
        "may_follow_up": admin.VERTICAL,
        "may_call_work": admin.VERTICAL,
        "may_contact_someone": admin.VERTICAL,
        "has_caretaker_alt": admin.VERTICAL,

    }
