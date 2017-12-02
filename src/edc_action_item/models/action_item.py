from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.deletion import PROTECT
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_constants.constants import NEW
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin

from ..choices import ACTION_STATUS, PRIORITY
from ..identifiers import ActionIdentifier
from .action_type import ActionType


class ActionItemUpdatesRequireFollowup(Exception):
    pass


class SubjectDoesNotExist(Exception):
    pass


class ActionItemManager(models.Manager):

    def get_by_natural_key(self, action_identifier):
        return self.get(action_identifier=action_identifier)


class ActionItem(NonUniqueSubjectIdentifierFieldMixin, BaseUuidModel):

    subject_identifier_model = 'edc_registration.registeredsubject'

    action_identifier = models.CharField(
        max_length=25,
        unique=True)

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    action_type = models.OneToOneField(
        ActionType, on_delete=PROTECT,
        related_name='action_type',
        verbose_name='Action')

    name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Leave blank to use the action type name.')

    priority = models.CharField(
        max_length=25,
        choices=PRIORITY,
        null=True,
        blank=True,
        help_text='Leave blank to use default for this action type.')

    parent_action = models.OneToOneField(
        'self', on_delete=PROTECT,
        null=True,
        blank=True)

    status = models.CharField(
        max_length=25,
        default=NEW,
        choices=ACTION_STATUS)

    next_action_type = models.OneToOneField(
        ActionType, on_delete=PROTECT,
        related_name='next_action_type',
        verbose_name='Next action',
        null=True,
        blank=True)

    auto_created = models.BooleanField(
        default=False)

    auto_created_comment = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    objects = ActionItemManager()

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.action_identifier[-9:]} {self.action_type.name}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.action_identifier = ActionIdentifier().identifier
            model_cls = django_apps.get_model(self.subject_identifier_model)
            try:
                model_cls.objects.get(
                    subject_identifier=self.subject_identifier)
            except ObjectDoesNotExist:
                raise SubjectDoesNotExist(
                    f'Invalid subject identifier. Subject does not exist. '
                    f'Got \'{self.subject_identifier}\'')
        self.priority = self.priority or self.action_type.priority
        super().save(*args, **kwargs)

    @property
    def last_updated(self):
        obj = self.actionitemupdate_set.all().order_by('report_datetime').last()
        if obj:
            return obj.report_datetime
        return None

    @property
    def user_last_updated(self):
        return self.user_modified or self.user_created

    def identifier(self):
        """Returns a shortened action identifier.
        """
        return self.action_identifier[-9:]

    @property
    def dashboard(self):
        url = reverse(settings.DASHBOARD_URL_NAMES.get("subject_dashboard_url"),
                      kwargs=dict(subject_identifier=self.subject_identifier))
        return mark_safe(
            f'<a data-toggle="tooltip" title="go to subject dashboard" '
            f'href="{url}">{self.subject_identifier}</a>')

    def natural_key(self):
        return (self.action_identifier, )
