from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from ..admin_site import edc_auth_admin

# admin.site.unregister(Group)
# admin.site.register(Group, GroupAdmin, site=edc_auth_admin)
