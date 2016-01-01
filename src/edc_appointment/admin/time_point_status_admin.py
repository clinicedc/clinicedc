from django.contrib import admin

from edc_appointment.models import Appointment

from ..forms import TimePointStatusForm
from ..models import TimePointStatus


class TimePointStatusAdmin(admin.ModelAdmin):

    form = TimePointStatusForm

    def __init__(self, *args, **kwargs):
        super(TimePointStatusAdmin, self).__init__(*args, **kwargs)
        self.list_display = (
            'dashboard',
            'close_datetime',
            'status',
            'subject_withdrew')
        self.search_fields.insert(0, 'appointment__registered_subject__subject_identifier')
        self.list_filter = (
            'status',
            'close_datetime',
            'appointment__registered_subject__gender',
            'appointment__visit_definition__code',
            'subject_withdrew',
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "appointment":
            if request.GET.get('appointment'):
                kwargs["queryset"] = Appointment.objects.filter(pk=request.GET.get('appointment'))
        return super(TimePointStatusAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(TimePointStatus, TimePointStatusAdmin)
