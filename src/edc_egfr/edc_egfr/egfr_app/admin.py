from django.contrib import admin

from edc_egfr.admin import EgfrDropNotificationAdminMixin

from .models import EgfrDropNotification


@admin.register(EgfrDropNotification)
class EgfrDropNotificationAdmin(EgfrDropNotificationAdminMixin, admin.ModelAdmin):
    pass
