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
            'subject_phone_alt',
            'subject_work_place',
            'subject_work_phone')})
)


indirect_contacts_fieldset = (
    ('Indirect Contact Information', {
        'fields': (
            'subject_work_phone',
            'indirect_contact_name',
            'indirect_contact_relation',
            'indirect_contact_physical_address',
            'indirect_contact_cell',
            'indirect_contact_cell_alt',
            'indirect_contact_phone')})
)
