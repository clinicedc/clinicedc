from django.contrib.admin.sites import AdminSite
from django.core.urlresolvers import reverse

from edc_rule_groups.site_rule_groups import site_rule_groups

from .constants import REQUIRED


class EdcMetaDataAdminSite(AdminSite):
    site_header = 'Edc Metadata'
    site_title = 'Edc Metadata'
    index_title = 'Edc Metadata Administration'
    site_url = '/edc-metadata/'
edc_metadata_admin = EdcMetaDataAdminSite(name='edc_metadata_admin')


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
