from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.deletion import PROTECT
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_base import get_utcnow
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites import CurrentSiteManager, SiteModelMixin
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


class ActionItem(NonUniqueSubjectIdentifierFieldMixin, SiteModelMixin,
                 BaseUuidModel):

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

    reference_model = models.CharField(
        max_length=50,
        null=True)

    linked_to_reference = models.BooleanField(
        default=False,
        editable=False,
        help_text=(
            'True if this action is linked to it\'s reference_model.'
            'Initially False if this action is created before reference_model.'
            'Always True when reference_model creates the action.'
            'Set to True when reference_model is created and "links" to this action.'
            '(Note: reference_model looks for actions where '
            'linked_to_reference is False before attempting to '
            'create a new ActionItem).'))

    related_reference_model = models.CharField(
        max_length=100,
        null=True,
        editable=False)

    related_reference_identifier = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=('May be left blank. e.g. action identifier from '
                   'source model that opened the item.'))

    parent_reference_model = models.CharField(
        max_length=100,
        null=True,
        editable=False)

    parent_reference_identifier = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=('May be left blank. e.g. action identifier from '
                   'reference model that opened the item (parent).'))

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

    on_site = CurrentSiteManager()

    objects = ActionItemManager()

    history = HistoricalRecords()

    def __str__(self):
        return (f'{self.action_type.display_name} {self.action_identifier[-9:]} '
                f'({self.get_status_display()})')

    def save(self, *args, **kwargs):
        """See also signals and action_cls.
        """
        if not self.id:
            # a new persisted action item always has
            # a unique action identifier
            self.action_identifier = ActionIdentifier().identifier
            # subject_identifier
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
            self.reference_model = self.action_type.reference_model
            self.related_reference_model = self.action_type.related_reference_model
            self.instructions = self.action_type.instructions
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier, )
    natural_key.dependencies = ['sites.Site']

    @property
    def last_updated(self):
        return None if self.status == NEW else self.modified

    @property
    def user_last_updated(self):
        return None if self.status == NEW else self.user_modified or self.user_created

    @property
    def action_cls(self):
        """Returns the action_cls.
        """
        return site_action_items.get(self.action_type.name)

    @property
    def action(self):
        """Returns the instantiated action_cls.
        """
        return self.action_cls(action_identifier=self.action_identifier)

    @property
    def reference_model_cls(self):
        return django_apps.get_model(self.reference_model)

    @property
    def reference_obj(self):
        return self.reference_model_cls.objects.get(
            action_identifier=self.action_identifier)

    @property
    def parent_reference_model_cls(self):
        return django_apps.get_model(self.parent_reference_model)

    @property
    def parent_reference_obj(self):
        """Returns the parent reference model instance.
        """
        return self.parent_reference_model_cls.objects.get(
            action_identifier=self.parent_reference_identifier)

    @property
    def related_reference_obj(self):
        """Returns the related reference model instance
        or raises ObjectDoesNotExist.
        """
        return django_apps.get_model(self.related_reference_model).objects.get(
            action_identifier=self.related_reference_identifier)

    @property
    def related_reference_model_cls(self):
        """Returns the related reference model instance.
        """
        return django_apps.get_model(self.related_reference_model)

    @property
    def identifier(self):
        """Returns a shortened action identifier.
        """
        return self.action_identifier[-9:]

    @property
    def parent(self):
        """Returns a url to the parent action item
        for display in admin.
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
        """Returns a shortened action_identifier which in
        most cases is the reference model's action identifier.
        """
        if self.action_identifier:
            return self.action_identifier[-9:]
        return None

    @property
    def parent_reference(self):
        """Returns a shortened parent_reference_identifier of the
        parent model reference which in most cases is the
        parent reference model's action identifier.
        """
        try:
            parent_reference = self.parent_action_item.action_identifier
        except AttributeError:
            parent_reference = None
        if parent_reference:
            return parent_reference[-9:]
        return None

    @property
    def related_reference(self):
        """Returns a shortened related_reference_identifier of the
        parent model reference which in most cases is the
        parent reference model's action identifier.
        """
        try:
            related_reference = self._related_reference_identifier
        except AttributeError:
            related_reference = None
        if related_reference:
            return related_reference[-9:]
        return None

    class Meta:
        verbose_name = 'Action Item'
        verbose_name_plural = 'Action Items'
