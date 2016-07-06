# from datetime import timedelta
# 
# from django.core.exceptions import ValidationError, ImproperlyConfigured
# from django.core.validators import MaxLengthValidator
# from django.db import models
# 
# from edc_base.model.models import BaseUuidModel
# from edc_content_type_map.models import ContentTypeMap
# 
# from .choices import VISIT_INTERVAL_UNITS
# from .managers import MembershipFormManager, VisitDefinitionManager
# from .utils import get_lower_window_days, get_upper_window_days
# 
# 
# class WindowPeriodMixin(models.Model):
# 
#     """Base Model of fields that define a window period, either for visits or forms."""
# 
#     time_point = models.IntegerField(
#         verbose_name="Time point",
#         default=0)
# 
#     base_interval = models.IntegerField(
#         verbose_name="Base interval",
#         help_text='Interval from base timepoint 0 as an integer.',
#         default=0)
# 
#     base_interval_unit = models.CharField(
#         max_length=10,
#         verbose_name="Base interval unit",
#         choices=VISIT_INTERVAL_UNITS,
#         default='D')
# 
#     lower_window = models.IntegerField(
#         verbose_name="Window lower bound",
#         default=0)
# 
#     lower_window_unit = models.CharField(
#         max_length=10,
#         verbose_name="Lower bound units",
#         choices=VISIT_INTERVAL_UNITS,
#         default='D')
# 
#     upper_window = models.IntegerField(
#         verbose_name="Window upper bound",
#         default=0)
# 
#     upper_window_unit = models.CharField(
#         max_length=10,
#         verbose_name="Upper bound units",
#         choices=VISIT_INTERVAL_UNITS,
#         default='D')
# 
#     grouping = models.CharField(
#         verbose_name='Grouping',
#         max_length=25,
#         null=True,
#         blank=True)
# 
#     def get_rdelta_attrname(self, unit):
#         if unit == 'H':
#             rdelta_attr_name = 'hours'
#         elif unit == 'D':
#             rdelta_attr_name = 'days'
#         elif unit == 'M':
#             rdelta_attr_name = 'months'
#         elif unit == 'Y':
#             rdelta_attr_name = 'years'
#         else:
#             raise TypeError('Unknown value for visit_definition.upper_window_unit. '
#                             'Expected [H, D, M, Y]. Got {0}.'.format(unit))
#         return rdelta_attr_name
# 
#     class Meta:
#         abstract = True
# 
# 
# class MembershipForm(BaseUuidModel):
# 
#     """Model to list forms to be linked to a Schedule as
#     "registration" forms to that group"""
# 
#     content_type_map = models.OneToOneField(
#         ContentTypeMap,
#         related_name='+')
# 
#     category = models.CharField(
#         max_length=35,
#         default='subject',
#         null=True,
#         help_text='In lowercase, this should be a valid subject type (as in registered_subject).',
#         unique=True)
# 
#     visible = models.BooleanField(
#         default=True,
#         help_text='If not visible on the dashboard, you have to write code to populate it yourself.')
# 
#     app_label = models.CharField(max_length=25, null=True)
# 
#     model_name = models.CharField(max_length=25, null=True)
# 
#     objects = MembershipFormManager()
# 
#     def save(self, *args, **kwargs):
#         from edc_appointment.mixins import AppointmentMixin
#         if not self.app_label:
#             self.app_label = self.content_type_map.app_label
#         if not self.model_name:
#             self.model_name = self.content_type_map.model
#         # get the model class
#         cls = self.content_type_map.model_class()
#         # inspect for registered subject attribute
#         if 'registered_subject' not in dir(cls):
#             raise ValidationError(
#                 'Membership forms must have a key to model RegisteredSubject. Got {0}'.format(cls))
#         if not issubclass(cls, AppointmentMixin):
#             raise ImproperlyConfigured(
#                 'MembershipForm attribute content_type_map must refer '
#                 'to a model class that is a subclass of AppointmentMixin. Got {0}'.format(cls))
#         super(MembershipForm, self).save(*args, **kwargs)
# 
#     def natural_key(self):
#         return self.content_type_map.natural_key()
# 
#     def __str__(self):
#         return self.content_type_map.name
# 
#     class Meta:
#         app_label = "edc_visit_schedule"
# 
# 
# class ScheduleManager(models.Manager):
# 
#     def get_by_natural_key(self, group_name):
#         return self.get(group_name=group_name)
# 
# 
# class Schedule(BaseUuidModel):
#     """Model that groups membership forms"""
# 
#     group_name = models.CharField(
#         max_length=25,
#         unique=True)
# 
#     membership_form = models.ForeignKey(MembershipForm)
# 
#     grouping_key = models.CharField(
#         max_length=25,
#         null=True,
#         blank=True,
#         help_text=(
#             'may specify a common value to group a number of membership forms so '
#             'that when one of the group is keyed, the others are no longer shown.'))
# 
#     comment = models.CharField(
#         max_length=25,
#         null=True,
#         blank=True)
# 
#     objects = ScheduleManager()
# 
#     def natural_key(self):
#         return (self.group_name, )
# 
#     def __str__(self):
#         return self.group_name
# 
#     class Meta:
#         ordering = ['group_name']
#         app_label = "edc_visit_schedule"
# 
# 
# def is_visit_tracking_model(value):
#     from edc_visit_tracking.models import VisitModelMixin
#     content_type_map = ContentTypeMap.objects.get(pk=value)
#     if not issubclass(content_type_map.model_class(), VisitModelMixin):
#         raise ValidationError('Select a model that is a subclass of VisitModelMixin')
# 
# 
# class VisitDefinition(WindowPeriodMixin, BaseUuidModel):
#     """Model to define a visit code, title, windows, schedule, etc."""
# 
#     code = models.CharField(
#         max_length=6,
#         validators=[MaxLengthValidator(6)],
#         db_index=True,
#         unique=True)
# 
#     title = models.CharField(
#         verbose_name="Title",
#         max_length=35,
#         db_index=True)
# 
#     visit_tracking_content_type_map = models.ForeignKey(
#         ContentTypeMap,
#         related_name='+',
#         null=True,
#         verbose_name='Visit Tracking Model',
#         validators=[is_visit_tracking_model, ])
# 
#     schedule = models.ManyToManyField(
#         Schedule,
#         blank=True,
#         help_text="Visit definition may be used in more than one schedule")
# 
#     instruction = models.TextField(
#         verbose_name="Instructions",
#         max_length=255,
#         blank=True)
# 
#     objects = VisitDefinitionManager()
# 
#     def __str__(self):
#         return '{0}: {1}'.format(self.code, self.title)
# 
#     def natural_key(self):
#         return (self.code, )
# 
#     def get_lower_window_datetime(self, appt_datetime):
#         if not appt_datetime:
#             return None
#         days = get_lower_window_days(self.lower_window, self.lower_window_unit)
#         td = timedelta(days=days)
#         return appt_datetime - td
# 
#     def get_upper_window_datetime(self, appt_datetime):
#         if not appt_datetime:
#             return None
#         days = get_upper_window_days(self.upper_window, self.upper_window_unit)
#         td = timedelta(days=days)
#         return appt_datetime + td
# 
#     class Meta:
#         ordering = ['code', 'time_point']
#         app_label = "edc_visit_schedule"
