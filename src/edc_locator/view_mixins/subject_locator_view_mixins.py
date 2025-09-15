from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from edc_action_item.site_action_items import site_action_items

from ..action_items import SUBJECT_LOCATOR_ACTION
from ..exceptions import SubjectLocatorViewMixinError
from ..utils import get_locator_model

if TYPE_CHECKING:
    from ..models import SubjectLocator


class SubjectLocatorViewMixin:
    """Adds subject locator to the context.

    Declare with RegisteredSubjectViewMixin.
    """

    subject_locator_model: int = get_locator_model()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.subject_locator_model:
            raise SubjectLocatorViewMixinError(
                "subject_locator_model must be a model (label_lower). Got None"
            )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        subject_locator = self.subject_locator
        if not subject_locator:
            subject_locator = self.subject_locator_model_cls(
                subject_identifier=self.subject_identifier
            )
            self.create_subject_locator_action()
        kwargs.update(subject_locator=subject_locator)
        return super().get_context_data(**kwargs)

    def create_subject_locator_action(self) -> None:
        """Create a subject locator action"""

        # kwargs `subject_identifier` updated by RegisteredSubject
        # view mixin get()
        subject_identifier = self.kwargs.get("subject_identifier")
        action_cls = site_action_items.get(SUBJECT_LOCATOR_ACTION)
        action_item_model_cls = action_cls.action_item_model_cls()
        try:
            action_item_model_cls.objects.get(
                subject_identifier=subject_identifier,
                action_type__name=SUBJECT_LOCATOR_ACTION,
            )
        except ObjectDoesNotExist:
            # only create missing action item if user has change perms
            app_label, model_name = self.subject_locator_model_cls._meta.label_lower.split(".")
            if self.request.user.has_perm(f"{app_label}.change_{model_name}"):
                action_cls(subject_identifier=subject_identifier)
        except MultipleObjectsReturned:
            # if condition exists, correct here
            action_item_model_cls.objects.filter(
                subject_identifier=subject_identifier,
                action_type__name=SUBJECT_LOCATOR_ACTION,
            ).delete()
            action_cls(subject_identifier=subject_identifier)

    @property
    def subject_locator_model_cls(self) -> type[SubjectLocator]:
        return django_apps.get_model(self.subject_locator_model)

    @property
    def subject_locator(self) -> SubjectLocator | None:
        """Returns a model instance or None"""
        try:
            obj = self.subject_locator_model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            obj = None
        return obj
