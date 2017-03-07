from django.contrib.admin import AdminSite


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
