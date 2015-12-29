from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from ..models import Review


class ReviewAdmin(BaseModelAdmin):
    list_display = ('title', 'review_status')
    fields = ('title', 'review_status', 'comment')
    search_fields = ('title', 'comment')
    list_filter = ('review_status',)
    readonly_fields = ('title', 'review_status')
admin.site.register(Review, ReviewAdmin)
