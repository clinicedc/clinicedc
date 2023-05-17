from django.contrib import admin
from django.utils.html import format_html
from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_auth_admin
from ..forms import UserProfileForm
from ..models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User profile"

    form = UserProfileForm

    filter_horizontal = ("email_notifications", "sms_notifications", "sites", "roles")


@admin.register(UserProfile, site=edc_auth_admin)
class UserProfileAdmin(TemplatesModelAdminMixin, admin.ModelAdmin):
    filter_horizontal = ("email_notifications", "sms_notifications", "sites")

    list_display = (
        "user",
        "user_sites",
        "user_email_notifications",
        "user_sms_notifications",
        "mobile",
        "export_format",
    )

    list_filter = ("sites__name", "email_notifications__name")

    search_fields = ("user__username", "mobile", "user__email")

    @staticmethod
    def user_sites(obj=None):
        site_names = [o.name for o in obj.sites.all().order_by("name")]
        return format_html("<BR>".join(site_names))

    @staticmethod
    def user_email_notifications(obj=None):
        display_names = [
            o.display_name for o in obj.email_notifications.all().order_by("display_name")
        ]
        return format_html("<BR>".join(display_names))

    @staticmethod
    def user_sms_notifications(obj=None):
        display_names = [
            o.display_name for o in obj.sms_notifications.all().order_by("display_name")
        ]
        return format_html("<BR>".join(display_names))
