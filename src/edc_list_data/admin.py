from django.contrib import admin


class ListModelAdminMixin(admin.ModelAdmin):

    ordering = ("display_index", "name")

    list_display = ["name", "short_name", "display_index"]

    search_fields = ("name", "short_name")
