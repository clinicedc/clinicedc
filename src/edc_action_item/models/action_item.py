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

from ..admin_site import edc_action_item_admin
from ..choices import ACTION_STATUS, PRIORITY
from ..identifiers import ActionIdentifier
from ..site_action_items import site_action_items
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

    action_type = models.ForeignKey(
        ActionType, on_delete=PROTECT,
        related_name='action_type',
        verbose_name='Action')

    reference_identifier = models.CharField(
        max_length=50,
        null=True,
        help_text='e.g. tracking identifier updated from the reference model')

    reference_model = models.CharField(
        max_length=50,
        null=True)

    parent_reference_identifier = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=('May be left blank. e.g. tracking identifier from '
                   'source model that opened the item.'))

    parent_model = models.CharField(
        max_length=100,
        null=True,
        editable=False)

    priority = models.CharField(
        max_length=25,
        choices=PRIORITY,
        null=True,
        blank=True,
        help_text='Leave blank to use default for this action type.')

    parent_action_item = models.ForeignKey(
        'self', on_delete=PROTECT,
        null=True,
        blank=True)

    status = models.CharField(
        max_length=25,
        default=NEW,
        choices=ACTION_STATUS)

    instructions = models.TextField(
        null=True,
        blank=True,
        help_text='populated by action class')

    auto_created = models.BooleanField(
        default=False)

    auto_created_comment = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    objects = ActionItemManager()

    history = HistoricalRecords()

    def __str__(self):
        return (f'{self.action_identifier[-9:]} {self.action_type.name} '
                f'({self.get_status_display()})')

    def save(self, *args, **kwargs):
        if not self.id:
            self.action_identifier = ActionIdentifier().identifier
            subject_identifier_model_cls = django_apps.get_model(
                self.subject_identifier_model)
            try:
                subject_identifier_model_cls.objects.get(
                    subject_identifier=self.subject_identifier)
            except ObjectDoesNotExist:
                raise SubjectDoesNotExist(
                    f'Invalid subject identifier. Subject does not exist '
                    f'in \'{self.subject_identifier_model}\'. '
                    f'Got \'{self.subject_identifier}\'.')
        self.priority = self.priority or self.action_type.priority
        self.reference_model = self.action_type.model
        if self.action:
            self.instructions = self.action.instructions
        super().save(*args, **kwargs)

    @property
    def last_updated(self):
        obj = self.actionitemupdate_set.all().order_by('report_datetime').last()
        if obj:
            return obj.modified
        return None if self.status == NEW else self.modified

    @property
    def user_last_updated(self):
        return self.user_modified or self.user_created

    @property
    def action(self):
        return site_action_items.get(self.action_type.name)

    @property
    def parent_object(self):
        """Returns the parent model instance or None.
        """
        if self.parent_model:
            return django_apps.get_model(self.parent_model).objects.get(
                tracking_identifier=self.parent_reference_identifier)
        return None

    @property
    def identifier(self):
        """Returns a shortened action identifier.
        """
        return self.action_identifier[-9:]

    @property
    def parent(self):
        """Returns a shortened parent tracking identifier.
        """
        if self.parent_action_item:
            url_name = '_'.join(self._meta.label_lower.split('.'))
            namespace = edc_action_item_admin.name
            url = reverse(
                f'{namespace}:{url_name}_changelist')
            return mark_safe(
                f'<a data-toggle="tooltip" title="go to parent action item" '
                f'href="{url}?q={self.parent_action_item.action_identifier}">'
                f'{self.parent_action_item.identifier}</a>')
        return None

    @property
    def reference(self):
        if self.reference_identifier:
            return self.reference_identifier[-9:]
        return None

    @property
    def parent_reference(self):
        if self.parent_reference_identifier:
            return self.parent_reference_identifier[-9:]
        return None

    @property
    def dashboard(self):
        url = reverse(settings.DASHBOARD_URL_NAMES.get("subject_dashboard_url"),
                      kwargs=dict(subject_identifier=self.subject_identifier))
        return mark_safe(
            f'<a data-toggle="tooltip" title="go to subject dashboard" '
            f'href="{url}">{self.subject_identifier}</a>')

    def natural_key(self):
        return (self.action_identifier, )

    class Meta:
        unique_together = ('subject_identifier',
                           'action_type', 'reference_identifier')
