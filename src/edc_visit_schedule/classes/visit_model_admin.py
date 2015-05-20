# from django.core.urlresolvers import reverse
# from edc.core.bhp_common.models import MyModelAdmin
# from edc.entry_meta_data.models import ScheduledEntryMetaData 
# 
# # this is not used, see bhp_appointment
# 
# class VisitModelAdmin (MyModelAdmin):
# 
#     """ModelAdmin subclass for models with a ForeignKey to 'visit'.
# 
#     Takes care of updating the bucket and redirecting back to the dashboard after
#     delete()
# 
#     """
#     def __init__(self, *args, **kwargs):
# 
#         super(VisitModelAdmin, self).__init__(*args, **kwargs)
#         self.list_filter
# 
#     def save_model(self, request, obj, form, change):
#         """Updates the scheduled entry bucket."""
#         ScheduledEntryMetaData.objects.update_status(
#             model=obj,
#             subject_visit_model=obj.visit,
#             )
# 
#         return super(VisitModelAdmin, self).save_model(request, obj, form, change)
# 
#     def delete_model(self, request, obj):
# 
#         ScheduledEntryMetaData.objects.update_status(
#             model=obj,
#             action='delete',
#             subject_visit_model=obj.visit,
#             )
# 
#         return super(VisitModelAdmin, self).delete_model(request, obj)
# 
#     def delete_view(self, request, object_id, extra_context=None):
# 
#         """ get a reverse url. delete_view requires knowledge of the model which is not given, so get it from the form.__dict__ and reverse resolve"""
#         # getting these two values this way works but seems a bit crazy ...
#         # TODO: this cannot work
#         subject_identifier = self.model.objects.get(pk=object_id).visit.appointment.registered_subject.subject_identifier
#         visit_code = self.model.objects.get(pk=object_id).visit.appointment.visit_definition.code
#         result = super(VisitModelAdmin, self).delete_view(request, object_id, extra_context)
# 
#         # hmmm. this is no good, need to get url_name from querystring
#         result['Location'] = reverse('subject_dashboard_visit_url', kwargs={'dashboard_type': request.GET.get('dashboard_type'),
#                                                                             'subject_identifier': subject_identifier,
#                                                                             'visit_code': unicode(visit_code)})
#         return result
