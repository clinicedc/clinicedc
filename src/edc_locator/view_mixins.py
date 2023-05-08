from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from edc_action_item.site_action_items import site_action_items

from .action_items import SUBJECT_LOCATOR_ACTION


class SubjectLocatorViewMixinError(Exception):
    pass


class SubjectLocatorViewMixin:

    """Adds subject locator to the context.

    Declare with SubjectIdentifierViewMixin.
    """

    subject_locator_model_wrapper_cls = None
    subject_locator_model = None

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wrapper = self.subject_locator_model_wrapper_cls(model_obj=self.subject_locator)
        context.update(subject_locator=wrapper)
        self.get_subject_locator_or_message()
        return context

    def get_subject_locator_or_message(self):
        obj = None
        subject_identifier = self.kwargs.get("subject_identifier")
        try:
            obj = self.subject_locator_model_cls.objects.get(
                subject_identifier=subject_identifier
            )
        except ObjectDoesNotExist:
            action_cls = site_action_items.get(SUBJECT_LOCATOR_ACTION)
            action_item_model_cls = action_cls.action_item_model_cls()
            try:
                action_item_model_cls.objects.get(
                    subject_identifier=subject_identifier,
                    action_type__name=SUBJECT_LOCATOR_ACTION,
                )
            except ObjectDoesNotExist:
                action_cls(subject_identifier=subject_identifier)
            except MultipleObjectsReturned:
                # if condition exists, correct here
                action_item_model_cls.objects.filter(
                    subject_identifier=subject_identifier,
                    action_type__name=SUBJECT_LOCATOR_ACTION,
                ).delete()
                action_cls(subject_identifier=subject_identifier)
        return obj

    @property
    def subject_locator_model_cls(self):
        try:
            model_cls = django_apps.get_model(self.subject_locator_model)
        except LookupError as e:
            raise SubjectLocatorViewMixinError(
                f"Unable to lookup subject locator model. "
                f"model={self.subject_locator_model}. Got {e}"
            )
        return model_cls

    @property
    def subject_locator(self):
        """Returns a model instance either saved or unsaved.

        If a save instance does not exits, returns a new unsaved instance.
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
