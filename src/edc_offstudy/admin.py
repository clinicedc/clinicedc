from django.contrib.admin.decorators import register
from django.contrib import admin

from .admin_site import edc_offstudy_admin
from .models import SubjectOffstudy


@register(SubjectOffstudy, site=edc_offstudy_admin)
class SubjectOffstudyAdmin(admin.ModelAdmin):

    pass
