from django.contrib import admin


from .admin_mixins import RegisteredSubjectModelAdminMixin
from .admin_site import edc_registration_admin
from .models import RegisteredSubject


@admin.register(RegisteredSubject, site=edc_registration_admin)
class RegisteredSubjectAdmin(RegisteredSubjectModelAdminMixin, admin.ModelAdmin):
    pass
