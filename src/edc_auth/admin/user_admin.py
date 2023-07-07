from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from edc_dashboard import select_edc_template
from edc_model_admin.mixins import TemplatesModelAdminMixin

from ..admin_site import edc_auth_admin
from ..forms import UserChangeForm
from ..send_new_credentials_to_user import send_new_credentials_to_user
from .list_filters import CountriesListFilter, SitesListFilter
from .user_profile_admin import UserProfileInline

admin.site.unregister(User)


def send_new_credentials_to_user_action(modeladmin, request, queryset):  # noqa
    if request.user.has_perm("auth.change_user"):
        for obj in queryset:
            send_new_credentials_to_user(user=obj)
    else:
        messages.error(request, "You do not have permissions to run this action.")


send_new_credentials_to_user_action.short_description = "Reset password and email to user"


@admin.register(User, site=edc_auth_admin)
class UserAdmin(TemplatesModelAdminMixin, BaseUserAdmin):
    show_object_tools: bool = True

    inlines = (UserProfileInline,)
    form = UserChangeForm
    actions = [send_new_credentials_to_user_action]

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "sites",
        "is_staff",
        "is_active",
        "last_login",
    )

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
        CountriesListFilter,
        SitesListFilter,
        "userprofile__roles",
        "groups",
    )

    def get_inline_instances(self, request, obj=None):
        """Don't load inlines on add.

        Wait until after first post_save signal creates
        UserProfile.
        """
        inline_instances = []
        if obj is None:
            return inline_instances
        return super().get_inline_instances(request, obj=obj)

    @staticmethod
    def role(obj=None) -> str:
        roles = []
        role_group_names = []
        for role in obj.userprofile.roles.all():
            roles.append(role)
            role_group_names.extend([grp.name for grp in role.groups.all().order_by("name")])
        extra_groups = [obj for obj in obj.groups.all() if obj.name not in role_group_names]
        context = dict(
            role_names=[role.display_name for role in roles],
            extra_group_names=[grp.name.replace("_", " ") for grp in extra_groups],
        )
        template_obj = select_edc_template("user_role_description.html", "edc_auth")
        return render_to_string(template_obj.template.name, context)

    @staticmethod
    def sites(obj=None) -> str:
        country_sites = {}
        for site in obj.userprofile.sites.all().order_by("siteprofile__country", "name"):
            country_name = site.siteprofile.country.replace("_", " ").title()
            site_name = site.name.replace("_", " ").title()
            try:
                country_sites[country_name].append(site_name)
            except KeyError:
                country_sites[country_name] = [site_name]

        context = dict(country_sites=country_sites)
        template_obj = select_edc_template("user_country_sites.html", "edc_auth")
        return render_to_string(template_obj.template.name, context)

    @staticmethod
    def groups_in_role(obj=None) -> str:
        roles = []
        role_group_names = []
        for role in obj.userprofile.roles.all():
            roles.append(role)
            role_group_names.extend([grp.name for grp in role.groups.all().order_by("name")])
        extra_groups = [obj for obj in obj.groups.all() if obj.name not in role_group_names]
        context = dict(
            role_names=[role.display_name for role in roles],
            extra_group_names=[grp.name.replace("_", " ") for grp in extra_groups],
        )
        template_obj = select_edc_template("user_role_description.html", "edc_auth")
        return render_to_string(template_obj.template.name, context)
