from edc.base.modeladmin.admin import BaseModelAdmin
from edc.export.actions import export_as_csv_action
from edc.subject.appointment.models import Appointment
from ..models import RegisteredSubject
from django.core.exceptions import ImproperlyConfigured


class BaseRegisteredSubjectModelAdmin (BaseModelAdmin):

    """ModelAdmin subclass for models with a ForeignKey to 'registered_subject'

    Takes care of updating the bucket and redirecting back to the dashboard after
    delete()

    """
    date_hierarchy = 'created'

    search_fields = ['registered_subject__subject_identifier', 'registered_subject__sid']
    list_display = ['registered_subject', 'created', 'modified', 'user_created', 'user_modified', ]
    list_filter = [
        'registered_subject__gender',
        'registered_subject__study_site',
        'registered_subject__survival_status',
        'registered_subject__registration_datetime',
        'created',
        'modified',
        'user_created',
        'user_modified',
        'hostname_created',
        'hostname_modified',
    ]

    def save_model(self, request, obj, form, change):
        if 'registered_subject' not in [fld.name for fld in self.model._meta.fields]:
            raise ImproperlyConfigured('Missing attribute registered_subject.')
        return super(BaseRegisteredSubjectModelAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "appointment":
            if request.GET.get('appointment'):
                kwargs["queryset"] = Appointment.objects.filter(id__exact=request.GET.get('appointment'))
        if db_field.name == "registered_subject":
            if request.GET.get('registered_subject'):
                kwargs["queryset"] = RegisteredSubject.objects.filter(pk=request.GET.get('registered_subject'))
        return super(BaseRegisteredSubjectModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    actions = [
        export_as_csv_action(
            "CSV Export of registered_subject",
            fields=[],
            exclude=[],
            extra_fields=[
                {'subject_identifier': 'registered_subject__subject_identifier'},
                {'gender': 'registered_subject__gender'},
                {'dob': 'registered_subject__dob'},
                {'registered': 'registered_subject__registration_datetime'},
            ],
        )]
