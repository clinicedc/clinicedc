from edc.base.modeladmin.admin import BaseModelAdmin
from edc.export.actions import export_as_csv_action
from edc.subject.appointment.models import Appointment
from ..models import RegisteredSubject


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
#     def __init__(self, *args, **kwargs):
#         self.search_fields = ['registered_subject__subject_identifier', 'registered_subject__sid']
#         self.list_display = ['registered_subject', 'created', 'modified', 'user_created', 'user_modified', ]
#         self.list_filter = [
#             'registered_subject__gender',
#             'registered_subject__study_site',
#             'registered_subject__survival_status',
#             'registered_subject__registration_datetime',
#             'created',
#             'modified',
#             'user_created',
#             'user_modified',
#             'hostname_created',
#             'hostname_modified',
#             ]
# 
#         super(BaseRegisteredSubjectModelAdmin, self).__init__(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        # i am explicitly listing valid subclasses for now. in future when code has stabilized
        # might be able to remove this ... i just want to know who's coming in here.
        #if not issubclass(obj.__class__, (BaseRegisteredSubjectModel, BaseOffStudy, BaseDeathReport)):
        #    raise TypeError('%s is using BaseRegisteredSubjectModelAdmin but is not a subclasses of BaseRegisteredSubjectModel.' % (obj, ))

        if not 'registered_subject' in [fld.name for fld in self.model._meta.fields]:
            raise TypeError('%s is using BaseRegisteredSubjectModelAdmin but does not have a key to RegisteredSubject.' % (obj,))
        # note: appointments are create in the base model's save() method
        # as long as it inherets from BaseRegisteredSubjectModel()
        return super(BaseRegisteredSubjectModelAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "appointment":
            if request.GET.get('appointment'):
                kwargs["queryset"] = Appointment.objects.filter(id__exact=request.GET.get('appointment'))
        if db_field.name == "registered_subject":
            if request.GET.get('registered_subject'):
                kwargs["queryset"] = RegisteredSubject.objects.filter(pk=request.GET.get('registered_subject'))
        return super(BaseRegisteredSubjectModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    actions = [export_as_csv_action("CSV Export of registered_subject",
        fields=[],
        exclude=[],
        extra_fields=[
            {'subject_identifier': 'registered_subject__subject_identifier'},
            {'gender': 'registered_subject__gender'},
            {'dob': 'registered_subject__dob'},
            {'registered': 'registered_subject__registration_datetime'},
            ],
        )]
