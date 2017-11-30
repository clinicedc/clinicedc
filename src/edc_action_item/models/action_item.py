from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_constants.constants import NEW
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin

from ..choices import ACTION_STATUS
from ..identifiers import ActionIdentifier


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

    title = models.CharField(
        max_length=50)

    status = models.CharField(
        max_length=25,
        default=NEW,
        choices=ACTION_STATUS)

    auto_created = models.BooleanField(
        default=False)

    auto_created_comment = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    comment = models.TextField(
        max_length=250,
        null=True,
        blank=True)

    objects = ActionItemManager()

    history = HistoricalRecords()

    def __str__(self):
        return self.action_identifier

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
        super().save(*args, **kwargs)

    @property
    def dashboard(self):
        url = reverse(settings.DASHBOARD_URL_NAMES.get("subject_dashboard_url"),
                      kwargs=dict(subject_identifier=self.subject_identifier))
        return mark_safe(
            f'<a data-toggle="tooltip" title="go to subject dashboard" '
            f'href="{url}">{self.subject_identifier}</a>')

    def natural_key(self):
        return (self.action_identifier, )
