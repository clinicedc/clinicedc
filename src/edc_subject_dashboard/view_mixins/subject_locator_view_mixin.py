from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class SubjectLocatorViewMixin:

    subject_locator_model_wrapper_cls = None
    subject_locator_model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wrapper = self.subject_locator_model_wrapper_cls(
            model_obj=self.subject_locator)
        context.update(subject_locator=wrapper)
        return context

    @property
    def subject_locator_model_cls(self):
        return django_apps.get_model(self.subject_locator_model)

    @property
    def subject_locator(self):
        """Returns a model instance either saved or unsaved.

        If a save instance does not exits, returns a new unsaved instance.
        """
        try:
            subject_locator = self.subject_locator_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            subject_locator = self.subject_locator_model_cls(
                subject_identifier=self.subject_identifier)
        return subject_locator
