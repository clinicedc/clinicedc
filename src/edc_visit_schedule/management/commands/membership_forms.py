# from django.core.management.base import BaseCommand
# from edc.subject.edc_visit_schedule.models import MembershipForm
# 
# 
# class Command(BaseCommand):
# 
#     args = ''
#     help = ''
# #     option_list = BaseCommand.option_list + (
# #         make_option('--field',
# #             action='store_true',
# #             dest='field',
# #             default=False,
# #             help='app.model.fieldname to convert. Not case sensitive.'),
# #         )
# 
#     def handle(self, *args, **options):
#         from edc.subject.appointment_helper.models import BaseAppointmentMixin
#         codes_for_category = MembershipForm.objects.codes_for_category
#         categories = [membership_form.category for membership_form in MembershipForm.objects.all().order_by('category')]
#         categories = list(set(categories))
#         print 'check subclassing of membership forms ...'
#         print '(membership forms must be a subclass of BaseAppointmentMixin)'
#         for category in categories:
#             print ' \'{0}\' visits: {1}'.format(category, ', '.join(codes_for_category(membership_form.category)))
#             for membership_form in MembershipForm.objects.filter(category=category):
#                 msg = 'ok'
#                 if not issubclass(membership_form.content_type_map.model_class(), BaseAppointmentMixin):
#                     msg = '    **warning: not a subclass of BaseAppointmentMixin**'
#                 print '    \'{0}\'...{1}'.format(membership_form.content_type_map.name, msg)
# 
#         print 'Done.'
