from django.contrib import admin

from .base_model_admin import BaseModelAdmin
from edc_base.modeladmin.admin import BaseTabularInline

from ..forms import PreAppointmentContactForm
from ..models import PreAppointmentContact


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
    list_display = ('contact_datetime', 'is_contacted', 'information_provider', 'is_confirmed')
    list_filter = ('contact_datetime', 'is_contacted', 'information_provider', 'is_confirmed')
    search_fields = ('appointment_identifier', 'id')
    radio_fields = {"is_contacted": admin.VERTICAL}
admin.site.register(PreAppointmentContact, PreAppointmentContactAdmin)
