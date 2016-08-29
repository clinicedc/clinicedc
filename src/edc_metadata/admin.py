from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.core.urlresolvers import reverse

from edc_rule_groups.classes import site_rule_groups

from .constants import REQUIRED

# from .models import CrfEntry, LabEntry, RequisitionPanel


class EdcMetaDataAdminSite(AdminSite):
    site_header = 'Edc Metadata'
    site_title = 'Edc Metadata'
    index_title = 'Edc Metadata Administration'
    site_url = '/edc-meta-data/'
edc_meta_data_admin = EdcMetaDataAdminSite(name='edc_meta_data_admin')


# @admin.register(CrfEntry, site=edc_meta_data_admin)
# class CrfEntryAdminMixin(admin.ModelAdmin):
# 
#     search_fields = ('visit_definition__code', 'content_type_map__model', 'id')
#     list_display = (
#         'content_type_map', 'visit_definition', 'entry_order', 'default_entry_status',
#         'additional', 'entry_category', 'group_title')
#     list_filter = (
#         'entry_category', 'group_title', 'visit_definition__code', 'default_entry_status',
#         'additional', 'created', 'content_type_map__model',)
# 
# 
# class CrfEntryInline (admin.TabularInline):
#     model = CrfEntry
#     extra = 0
#     fields = (
#         'content_type_map',
#         'entry_order',
#         'default_entry_status',
#         'additional',
#         'entry_category',
#         'entry_window_calculation',
#         'group_title')
# 
# 
# @admin.register(LabEntry, site=edc_meta_data_admin)
# class LabEntryAdmin(admin.ModelAdmin):
# 
#     search_fields = ('visit_definition__code', 'requisition_panel__name')
# 
#     list_display = ('requisition_panel', 'visit_definition', 'entry_order',
#                     'default_entry_status', 'additional', 'entry_category')
# 
#     list_filter = ('entry_category', 'visit_definition__code', 'default_entry_status',
#                    'additional', 'created', 'requisition_panel__name',)
# 
# 
# class LabEntryInline (admin.TabularInline):
#     model = LabEntry
#     extra = 0
#     fields = (
#         'requisition_panel',
#         'entry_order',
#         'default_entry_status',
#         'additional',
#         'entry_category',
#         'entry_window_calculation',
#     )
# 
# 
# @admin.register(RequisitionPanel, site=edc_meta_data_admin)
# class RequisitionPanelAdmin(admin.ModelAdmin):
# 
#     search_fields = ('name', 'aliquot_type_alpha_code')
# 
#     list_display = ('name', 'aliquot_type_alpha_code')
# 
#     list_filter = ('aliquot_type_alpha_code',)
# 
# 
# class CrfMetaDataAdminMixin:
# 
#     search_fields = (
#         'registered_subject__subject_identifier', 'crf_entry__visit_definition__code',
#         'crf_entry__content_type_map__model', 'id')
#     list_display = (
#         'registered_subject', 'crf_entry', 'entry_status', 'fill_datetime',
#         'due_datetime', 'close_datetime', 'created', 'hostname_created')
#     list_filter = (
#         'entry_status', 'crf_entry__visit_definition__code', 'fill_datetime',
#         'created', 'user_created', 'hostname_created')
#     readonly_fields = ('registered_subject', 'appointment')
# 
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "crf_entry":
#             kwargs["queryset"] = CrfEntry.objects.filter(pk=request.GET.get('crf_entry'))
#         return super(CrfMetaDataAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)


# class RequisitionMetaDataAdminMixin:
# 
#     search_fields = (
#         'registered_subject__subject_identifier', 'lab_entry__visit_definition__code',
#         'lab_entry__requisition_panel__name', 'id')
#     list_display = (
#         'registered_subject', 'lab_entry', 'entry_status', 'fill_datetime', 'due_datetime', 'close_datetime')
#     list_filter = (
#         'entry_status', 'lab_entry__visit_definition__code', 'fill_datetime',
#         'created', 'user_created', 'hostname_created')
#     readonly_fields = ('registered_subject', 'appointment')
# 
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "lab_entry":
#             kwargs["queryset"] = LabEntry.objects.filter(pk=request.GET.get('lab_entry'))
#         return super(RequisitionMetaDataAdminMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ModelAdminCrfMetaDataMixin(object):

    crf_visit_attr = None  # e.g. subject_visit
    meta_data_model = None  # e.g. CrfMetaData
    entry_model = None  # CrfEntry
    entry_attr = None  # 'crf_entry'

    def next_url_from_crf_meta_data(self, request, obj):
        """Returns a tuple with the reverse of the admin url for the next
        model listed in crf_meta_data."""
        next_crf_url, visit_model_instance, entry_order = (None, None, None)
        visit = self.get_crf_visit(request, obj)
        if visit:
            site_rule_groups.update_rules_for_source_model(obj, visit)
            crf_meta_data_instance = self.get_next_entry_for(request, obj)
            if crf_meta_data_instance:
                next_crf_url, visit_model_instance, entry_order = (
                    reverse('admin:{0}_{1}_add'.format(
                        crf_meta_data_instance.crf_entry.content_type_map.app_label,
                        crf_meta_data_instance.crf_entry.content_type_map.module_name)),
                    visit,
                    crf_meta_data_instance.crf_entry.entry_order
                )
        return next_crf_url, visit_model_instance, entry_order

    def get_next_entry_for(self, request, obj):
        """Gets next meta data instance based on the given entry order,
        used with the save_next button on a form."""
        crf_meta_data_instance = None
        entry_order = request.GET.get('entry_order')
        visit = self.get_crf_visit(request, obj)
        options = {
            'registered_subject_id': visit.appointment.registered_subject.pk,
            'appointment_id': visit.appointment_zero.pk,
            'entry_status': REQUIRED,
            '{0}__entry_order__gt'.format(self.entry_attr): entry_order}
        if self.meta_data_model.objects.filter(**options):
            crf_meta_data_instance = self.meta_data_model.objects.filter(**options)[0]
        return crf_meta_data_instance

    def visit(self, request, obj):
        """Return the visit model instance or None."""
        try:
            visit = getattr(obj, self.crf_visit_attr or request.GET.get('visit_attr'))
        except AttributeError:
            visit = None
        return visit
