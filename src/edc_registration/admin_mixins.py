from edc_model_admin import ModelAdminBasicMixin


class RegisteredSubjectModelAdminMixin(ModelAdminBasicMixin):

    date_hierarchy = 'registration_datetime'

    mixin_list_display = (
        'subject_identifier',
        'first_name',
        'initials',
        'gender',
        'subject_type',
        'sid',
        'registration_status',
        'site',
        'user_created',
        'created',
    )

    mixin_readonly_fields = (
        'subject_identifier',
        'subject_identifier_as_pk',
    )

    mixin_search_fields = ('subject_identifier', 'first_name', 'initials',
                           'sid', 'identity', 'id', 'registration_identifier')

    mixin_list_filter = ('subject_type', 'registration_status', 'screening_datetime',
                         'registration_datetime', 'gender',
                         'site', 'hostname_created')
