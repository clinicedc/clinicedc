from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from edc_base.model.models import BaseUuidModel
from edc_content_type_map.models import ContentTypeMap

from ..managers import MemberManager


class Member(BaseUuidModel):

    """Model to list forms to be linked to a ScheduleGroup as
    "registration" forms to that group"""

    content_type_map = models.OneToOneField(
        ContentTypeMap,
        related_name='+'
    )

    category = models.CharField(
        max_length=35,
        default='subject',
        null=True,
        help_text='In lowercase, this should be a valid subject type (as in registered_subject).',
        unique=True,
    )

    visible = models.BooleanField(
        default=True,
        help_text='If not visible on the dashboard, you have to write code to populate it yourself.'
    )

    app_label = models.CharField(max_length=25, null=True)

    model_name = models.CharField(max_length=25, null=True)

    objects = MemberManager()

    def save(self, *args, **kwargs):
        if not self.app_label:
            self.app_label = self.content_type_map.app_label
        if not self.model_name:
            self.model_name = self.content_type_map.model
        if 'registered_subject' not in dir(self.registration_model):
            raise ValidationError(
                'Models listed in Member must have a key to model RegisteredSubject. '
                'Got {0}'.format(self.registration_model))
        super(Member, self).save(*args, **kwargs)

    def natural_key(self):
        return self.content_type_map.natural_key()

    @property
    def registration_model(self):
        """Returns a model class."""
        return self.content_type_map.model_class()

    def get_absolute_url(self):
        return reverse('admin:edc_visit_schedule_member_change', args=(self.id,))

    def __unicode__(self):
        return self.content_type_map.name

    class Meta:
        app_label = "edc_visit_schedule"
