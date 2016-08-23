

class AliquotModelAdminMixin:

    date_hierarchy = 'created'

    list_display = ("aliquot_identifier", 'subject_identifier',
                    'processing',  # 'related',
                    'to_receive', 'drawn', "aliquot_type",
                    'aliquot_condition', 'is_packed', 'created',
                    'user_created', 'hostname_created')

    search_fields = ('aliquot_identifier', 'receive__receive_identifier',
                     'receive__registered_subject__subject_identifier')

    list_filter = ('aliquot_type', 'aliquot_condition',
                   'created', 'user_created', 'hostname_created')

    list_per_page = 15


class AliquotTypeModelAdminMixin:

    list_display = ('name', 'alpha_code', 'numeric_code')


class AliquotProcessingModelAdminMixin:

    list_display = ('aliquot', 'profile', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('aliquot__aliquot_identifier', 'profile__profile_name', 'aliquot__aliquot_type__name', 'aliquot__aliquot_type__alpha_code', 'aliquot__aliquot_type__numeric_code')

    list_filter = ('profile', 'created', 'modified', 'user_created', 'user_modified')


class AliquotProfileModelAdminMixin:

    list_display = ('name', 'aliquot_type', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('name', 'aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code')

    list_filter = ('aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code', 'created', 'modified', 'user_created', 'user_modified')


class AliquotProfileItemModelAdminMixin:

    list_display = ('profile', 'aliquot_type', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('profile__profile_name', 'aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code')

    list_filter = ('aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code', 'created', 'modified', 'user_created', 'user_modified')
