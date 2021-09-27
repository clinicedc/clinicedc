from django.contrib import admin
from django.utils.safestring import mark_safe

from ..forms import UserProfileForm
from ..models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User profile"

    filter_horizontal = ("email_notifications", "sms_notifications", "sites", "roles")

    form = UserProfileForm


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    add_form = ""

    filter_horizontal = ("email_notifications", "sms_notifications", "sites")

    list_display = (
        "user",
        "user_sites",
        "user_email_notifications",
        "user_sms_notifications",
        "mobile",
        "export_format",
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    @staticmethod
    def user_sites(obj=None):

        return mark_safe(
            "<BR>".join([o.name for o in obj.sites.all().order_by("name")])
        )

    @staticmethod
    def user_email_notifications(obj=None):
        return mark_safe(
            "<BR>".join(
                [
                    o.display_name
                    for o in obj.email_notifications.all().order_by("display_name")
                ]
            )
        )

    @staticmethod
    def user_sms_notifications(obj=None):
        return mark_safe(
            "<BR>".join(
                [
                    o.display_name
                    for o in obj.sms_notifications.all().order_by("display_name")
                ]
            )
        )
