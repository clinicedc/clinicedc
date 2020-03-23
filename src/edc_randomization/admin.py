from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib import admin
from edc_model_admin.model_admin_audit_fields_mixin import (
    audit_fieldset_tuple,
    audit_fields,
)
from .admin_site import edc_randomization_admin
from .blinding import is_blinded_user
from .site_randomizers import site_randomizers

admin.site.disable_action("delete_selected")


class RandomizationListModelAdmin(admin.ModelAdmin):
    list_per_page = 15

    view_on_site = False

    ordering = ("sid",)

    list_filter = (
        "allocated_datetime",
        "allocated_site",
        "site_name",
        "randomizer_name",
    )

    search_fields = ("subject_identifier", "sid")

    readonly_fields = [
        "subject_identifier",
        "sid",
        "site_name",
        "assignment",
        "allocated",
        "allocated_user",
        "allocated_datetime",
        "allocated_site",
        "randomizer_name",
    ] + audit_fields

    def get_queryset(self, request):
        """
        Filter the changelist to show for this site_name only.
        """
        site = Site.objects.get(pk=settings.SITE_ID)
        qs = self.model.objects.filter(site_name=site.name)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_list_display(self, request):
        list_display = [
            "sid",
            "assignment",
            "site_name",
            "subject_identifier",
            "allocated_datetime",
            "allocated_site",
            "randomizer_name",
        ]
        if is_blinded_user(request.user.username):
            list_display.remove("assignment")
        return list_display

    def get_fieldnames(self, request):
        fields = [
            "subject_identifier",
            "sid",
            "assignment",
            "allocated",
            "allocated_user",
            "allocated_datetime",
            "allocated_site",
            "randomizer_name",
        ]
        if is_blinded_user(request.user.username):
            fields.remove("assignment")
        return fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {"fields": self.get_fieldnames(request)}),
            audit_fieldset_tuple,
        )
        return fieldsets


site_randomizers.autodiscover()

for randomizer_cls in site_randomizers._registry.values():
    model = randomizer_cls.model_cls()
    NewModelAdminClass = type(
        f"{model.__name__}ModelAdmin", (RandomizationListModelAdmin,), {}
    )
    edc_randomization_admin.register(model, NewModelAdminClass)
