from django.contrib import admin
from edc.base.modeladmin.admin import BaseModelAdmin
from edc.base.modeladmin.admin import BaseTabularInline
from edc_appointment import PreAppointmentContactForm
from edc_appointment import PreAppointmentContact


class PreAppointmentContactInlineAdmin(BaseTabularInline):
    model = PreAppointmentContact
    form = PreAppointmentContactForm
    extra = 0
    fields = ('contact_datetime', 'is_contacted', 'information_provider', 'is_confirmed', 'comment')
    radio_fields = {"is_contacted": admin.VERTICAL}


class PreAppointmentContactAdmin(BaseModelAdmin):
    form = PreAppointmentContactForm
    date_hierarchy = 'contact_datetime'
    fields = ('contact_datetime', 'is_contacted', 'information_provider', 'is_confirmed', 'comment')
    list_display = ('edc_appointment', 'contact_datetime', 'is_contacted', 'information_provider', 'is_confirmed')
    list_filter = ('contact_datetime', 'is_contacted', 'information_provider', 'is_confirmed')
    search_fields = ('appointment__registered_subject__subject_identifier', 'id', 'appointment__pk')
    radio_fields = {"is_contacted": admin.VERTICAL}
admin.site.register(PreAppointmentContact, PreAppointmentContactAdmin)
