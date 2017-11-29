from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = 'Edc Action Item'
    site_header = 'Edc Action Item'
    index_title = 'Edc Action Item'
    site_url = '/administration/'


edc_action_item_admin = AdminSite(name='edc_action_item_admin')
