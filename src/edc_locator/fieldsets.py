subject_contacts_fieldset = (
    ('Subject Contact Information', {
        'fields': (
            'may_call',
            'may_visit_home',
            'may_sms',
            'mail_address',
            'physical_address',
            'subject_cell',
            'subject_cell_alt',
            'subject_phone',
            'subject_phone_alt')})
)


work_contacts_fieldset = (
    ('Subject\'s Work Contacts', {
        'fields': (
            'may_call_work',
            'subject_work_place',
            'subject_work_phone',
            'subject_work_cell')})
)

indirect_contacts_fieldset = (
    ('Other Contact Information', {
        'fields': (
            'may_contact_indirectly',
            'indirect_contact_name',
            'indirect_contact_relation',
            'indirect_contact_physical_address',
            'indirect_contact_cell',
            'indirect_contact_cell_alt',
            'indirect_contact_phone')})
)
