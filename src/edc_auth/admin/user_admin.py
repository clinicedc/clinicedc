from django.contrib import messages
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from edc_dashboard import select_edc_template

from ..admin_site import edc_auth_admin
from ..forms import UserChangeForm
from ..send_new_credentials_to_user import send_new_credentials_to_user
from .user_profile_admin import UserProfileInline


admin.site.unregister(User)


def send_new_credentials_to_user_action(modeladmin, request, queryset):
    if request.user.has_perms(["auth.change_user"]):
        for obj in queryset:
            send_new_credentials_to_user(user=obj, request=request)
    else:
        messages.error(request, "You do not have permissions to run this action.")


send_new_credentials_to_user_action.short_description = (
    "Reset password and email to user"
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    form = UserChangeForm
    actions = [send_new_credentials_to_user_action]

    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "userprofile__roles__name",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "userprofile__roles",
        "groups",
    )

    def role(self, obj=None):
        roles = []
        role_group_names = []
        for role in obj.userprofile.roles.all():
            roles.append(role)
            role_group_names.extend(
                [grp.name for grp in role.groups.all().order_by("name")]
            )
        extra_groups = [
            obj for obj in obj.groups.all() if obj.name not in role_group_names
        ]
        context = dict(
            role_names=[role.display_name for role in roles],
            extra_group_names=[grp.name.replace("_", " ") for grp in extra_groups],
        )
        template_obj = select_edc_template("user_role_description.html", "edc_auth")
        return render_to_string(template_obj.template.name, context)

    def groups_in_role(self, obj=None):
        roles = []
        role_group_names = []
        for role in obj.userprofile.roles.all():
            roles.append(role)
            role_group_names.extend(
                [grp.name for grp in role.groups.all().order_by("name")]
            )
        extra_groups = [
            obj for obj in obj.groups.all() if obj.name not in role_group_names
        ]
        context = dict(
            role_names=[role.display_name for role in roles],
            extra_group_names=[grp.name.replace("_", " ") for grp in extra_groups],
        )
        template_obj = select_edc_template("user_role_description.html", "edc_auth")
        return render_to_string(template_obj.template.name, context)
