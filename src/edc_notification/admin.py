from django.contrib.admin.decorators import register
from django.contrib import admin

from .admin_site import edc_notification_admin
from .models import Notification


@register(Notification, site=edc_notification_admin)
class NotificationAdmin(admin.ModelAdmin):

    model = Notification

    list_display = ("name", "display_name", "mailing_list_address")
