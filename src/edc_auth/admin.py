from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .forms import UserProfileForm
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User profile"

    filter_horizontal = ("email_notifications", "sms_notifications", "sites")

    form = UserProfileForm


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


class UserProfileAdmin(admin.ModelAdmin):

    filter_horizontal = ("email_notifications", "sms_notifications", "sites")

    list_display = (
        "user",
        "user_sites",
        "user_email_notifications",
        "user_sms_notifications",
        "mobile",
    )

    def user_sites(self, obj=None):
        return mark_safe(
            "<BR>".join([o.name for o in obj.sites.all().order_by("name")])
        )

    def user_email_notifications(self, obj=None):
        return mark_safe(
            "<BR>".join(
                [
                    o.display_name
                    for o in obj.email_notifications.all().order_by("display_name")
                ]
            )
        )

    def user_sms_notifications(self, obj=None):
        return mark_safe(
            "<BR>".join(
                [
                    o.display_name
                    for o in obj.sms_notifications.all().order_by("display_name")
                ]
            )
        )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
