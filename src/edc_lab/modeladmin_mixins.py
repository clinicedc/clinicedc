from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured

from .actions import flag_as_received, flag_as_not_received, flag_as_not_labelled, print_requisition_label


class AliquotModelAdminMixin(admin.ModelAdmin):

    date_hierarchy = 'created'

    list_display = ("aliquot_identifier", 'subject_identifier',
                    'processing',
                    'to_receive', 'drawn', "aliquot_type",
                    'aliquot_condition', 'is_packed', 'created',
                    'user_created', 'hostname_created')

    search_fields = ('aliquot_identifier', 'receive__receive_identifier',
                     'receive__registered_subject__subject_identifier')

    list_filter = ('aliquot_type', 'aliquot_condition',
                   'created', 'user_created', 'hostname_created')

    list_per_page = 15


class SpecimenCollectionItemModelAdminMixin(admin.ModelAdmin):

    date_hierarchy = 'created'

    list_per_page = 15


class SpecimenCollectionModelAdminMixin(admin.ModelAdmin):

    date_hierarchy = 'created'

    list_per_page = 15


class AliquotTypeModelAdminMixin(admin.ModelAdmin):

    list_display = ('name', 'alpha_code', 'numeric_code')


class AliquotProcessingModelAdminMixin:

    list_display = ('aliquot', 'profile', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('aliquot__aliquot_identifier', 'profile__profile_name', 'aliquot__aliquot_type__name', 'aliquot__aliquot_type__alpha_code', 'aliquot__aliquot_type__numeric_code')

    list_filter = ('profile', 'created', 'modified', 'user_created', 'user_modified')


class AliquotProfileModelAdminMixin(admin.ModelAdmin):

    list_display = ('name', 'aliquot_type', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('name', 'aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code')

    list_filter = ('aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code', 'created', 'modified', 'user_created', 'user_modified')


class AliquotProfileItemModelAdminMixin(admin.ModelAdmin):

    list_display = ('profile', 'aliquot_type', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('profile__profile_name', 'aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code')

    list_filter = ('aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code', 'created', 'modified', 'user_created', 'user_modified')


class PackingListModelAdminMixin(admin.ModelAdmin):

    fields = ('destination', 'list_items', 'list_comment',)

    list_display = (
        'reference',
        'view_list_items',
        'list_datetime',
        'list_comment',
        'destination',
        'received', )

    list_filter = (
        'list_datetime',
        'destination',
        'received',
        'list_comment')

    search_fields = ('id', 'list_comment')


class PackingListItemModelAdminMixin(admin.ModelAdmin):

    search_fields = ('packing_list__pk', 'packing_list__timestamp', 'item_description', 'item_reference', )
    list_display = ('specimen', 'priority', 'panel', 'description', 'gender',
                    'drawn_datetime', 'clinician', 'view_packing_list', 'received', 'received_datetime',)
    list_filter = ('created', 'panel', 'received', 'received_datetime',)

    def delete_model(self, request, obj):

        if not isinstance(self.subject_requisition, list):
            self.subject_requisition = [self.subject_requisition, ]
        for requisition in self.requisition:
            if requisition.objects.filter(specimen_identifier=obj.item_reference):
                subject_requisition = requisition.objects.get(specimen_identifier=obj.item_reference)
                subject_requisition.is_packed = False
                subject_requisition.save()
        super(PackingListItemModelAdminMixin, self).delete_model(request, obj)


class ReceiveModelAdminMixin(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        if obj:  # In edit mode
            return ('receive_identifier',) + self.readonly_fields
        else:
            return self.readonly_fields

    list_display = ('receive_identifier', 'drawn_datetime', 'receive_datetime')
    search_fields = ('receive_identifier', 'patient__subject_identifier')
    list_filter = ('drawn_datetime', 'receive_datetime')
    list_per_page = 15
    date_hierarchy = 'drawn_datetime'


class RequisitionAdminMixin:

    panel_model = None
    date_hierarchy = 'requisition_datetime'
    actions = [
        flag_as_received,
        flag_as_not_received,
        flag_as_not_labelled,
        print_requisition_label,
    ]

    def __init__(self, *args, **kwargs):
        if not self.panel_model:
            raise ImproperlyConfigured('{}.panel_model cannot be None.'.format(self.__class__.__name__))
        super(RequisitionAdminMixin, self).__init__(*args, **kwargs)

    fields = [
        "requisition_datetime",
        "is_drawn",
        "reason_not_drawn",
        "drawn_datetime",
        'study_site',
        "panel_name",
        "aliquot_type",
        "item_type",
        "item_count",
        "estimated_volume",
        "comments", ]

    radio_fields = {
        "is_drawn": admin.VERTICAL,
        "reason_not_drawn": admin.VERTICAL,
        "item_type": admin.VERTICAL,
    }

    list_display = [
        'requisition_identifier',
        'subject',
        'visit',
        "requisition_datetime",
        "panel",
        'aliquot',
        'hostname_created']

    list_filter = [
        'panel_name',
        "requisition_datetime",
        'study_site',
        'user_created',
        'hostname_created',
        'user_modified',
    ]

    search_fields = [
        'subject_identifier',
        'specimen_identifier',
        'requisition_identifier',
        'panel_name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        panel_pk = request.GET.get('panel', 0)
        if db_field.name == 'panel':
            kwargs["queryset"] = self.panel_model.objects.filter(pk=panel_pk)
        if db_field.name == 'aliquot_type':
            if self.panel_model.objects.filter(pk=panel_pk):
                if self.panel_model.objects.get(pk=panel_pk).aliquot_type.all():
                    kwargs["queryset"] = self.panel_model.objects.get(pk=panel_pk).aliquot_type.all()
        return super(RequisitionAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)
