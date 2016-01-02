from django.contrib import admin

from ..forms import TimePointStatusForm
from ..models import TimePointStatus


class TimePointStatusAdmin(admin.ModelAdmin):

    form = TimePointStatusForm

    fields = (
        'subject_identifier',
        'visit_code',
        'status',
        'subject_withdrew',
        'reasons_withdrawn',
        'withdraw_datetime',
        'comment'
    )

    list_display = (
        'subject_identifier',
        'visit_code',
        'dashboard',
        'close_datetime',
        'status',
        'subject_withdrew')

    list_filter = (
        'status',
        'close_datetime',
        'visit_code',
        'subject_withdrew')

    readonly_fields = (
        'subject_identifier',
        'visit_code',
    )

    radio_fields = {
        'status': admin.VERTICAL,
        'subject_withdrew': admin.VERTICAL,
        'reasons_withdrawn': admin.VERTICAL,
    }

admin.site.register(TimePointStatus, TimePointStatusAdmin)
