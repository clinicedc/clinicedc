from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type

from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from edc_action_item.site_action_items import site_action_items
from edc_sites.utils import get_user_codenames_or_raise

from .action_items import SUBJECT_LOCATOR_ACTION

if TYPE_CHECKING:
    from edc_model_wrapper import ModelWrapper

    from .models import SubjectLocator


class SubjectLocatorViewMixinError(Exception):
    pass


class SubjectLocatorViewMixin:

    """Adds subject locator to the context.

    Declare with SubjectIdentifierViewMixin.
    """

    subject_locator_model_wrapper_cls: Type[ModelWrapper] = None
    subject_locator_model: int = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.subject_locator_model_wrapper_cls:
            raise SubjectLocatorViewMixinError(
                "subject_locator_model_wrapper_cls must be a valid ModelWrapper. Got None"
            )
        if not self.subject_locator_model:
            raise SubjectLocatorViewMixinError(
                "subject_locator_model must be a model (label_lower). Got None"
            )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.create_subject_locator_action_if_required()
        wrapper = self.subject_locator_model_wrapper_cls(model_obj=self.subject_locator)
        kwargs.update(subject_locator=wrapper)
        return super().get_context_data(**kwargs)

    def create_subject_locator_action_if_required(self) -> None:
        """Create a subject locator action if the subject locator
        does not exist.

        Only check if user has change permissions.
        """

        # kwargs `subject_identifier` updated by RegisteredSubject
        # view mixin get()
        subject_identifier = self.kwargs.get("subject_identifier")
        try:
            self.subject_locator_model_cls.objects.get(subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            action_cls = site_action_items.get(SUBJECT_LOCATOR_ACTION)
            action_item_model_cls = action_cls.action_item_model_cls()
            try:
                action_item_model_cls.objects.get(
                    subject_identifier=subject_identifier,
                    action_type__name=SUBJECT_LOCATOR_ACTION,
                )
            except ObjectDoesNotExist:
                # only create missing action item if user has change perms
                _, model_name = self.subject_locator_model.split(".")
                if f"change_{model_name}" in get_user_codenames_or_raise(self.request.user):
                    action_cls(subject_identifier=subject_identifier)
            except MultipleObjectsReturned:
                # if condition exists, correct here
                action_item_model_cls.objects.filter(
                    subject_identifier=subject_identifier,
                    action_type__name=SUBJECT_LOCATOR_ACTION,
                ).delete()
                action_cls(subject_identifier=subject_identifier)

    @property
    def subject_locator_model_cls(self) -> Type[SubjectLocator]:
        try:
            model_cls = django_apps.get_model(self.subject_locator_model)
        except LookupError as e:
            raise SubjectLocatorViewMixinError(
                f"Unable to lookup subject locator model. "
                f"model={self.subject_locator_model}. Got {e}"
            )
        return model_cls

    @property
    def subject_locator(self) -> SubjectLocator:
        """Returns a model instance either saved or unsaved.

        If a saved instance does not exist, returns a new unsaved instance.
        """
        model_cls = self.subject_locator_model_cls
        try:
            subject_locator = model_cls.objects.get(
                subject_identifier=self.kwargs.get("subject_identifier")
            )
        except ObjectDoesNotExist:
            subject_locator = model_cls(
                subject_identifier=self.kwargs.get("subject_identifier")
            )
        return subject_locator
