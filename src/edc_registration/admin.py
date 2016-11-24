from django.contrib.admin import AdminSite

from edc_base.modeladmin_mixins import ModelAdminBasicMixin


class EdcRegistrationAdminSite(AdminSite):
    """
    For example:
        add to urls:
            url(r'^admin/edc_registration/', edc_registration_admin.urls),
        then:
            >>> reverse('edc_registration_admin:registration_registeredsubject_add')
            '/admin/registration/registeredsubject/add/'
    """
    site_header = 'Registration'
    site_title = 'Registration'
    index_title = 'Registration Administration'
    site_url = '/registration/'
edc_registration_admin = EdcRegistrationAdminSite(name='edc_registration_admin')


class RegisteredSubjectModelAdminMixin(ModelAdminBasicMixin):

    date_hierarchy = 'registration_datetime'

    mixin_list_display = (
        'subject_identifier',
        'dashboard',
        'first_name',
        'initials',
        'gender',
        'age',
        'subject_type',
        'sid',
        'registration_status',
        'study_site',
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
                         'study_site', 'hiv_status', 'survival_status',
                         'may_store_samples', 'hostname_created')
