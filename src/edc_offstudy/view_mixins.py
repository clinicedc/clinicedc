from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import ContextMixin


class SubjectOffstudyViewMixinError(Exception):
    pass


class SubjectOffstudyViewMixin(ContextMixin):

    """Adds subject offstudy to the context.

    Declare with SubjectIdentifierViewMixin.
    """

    offstudy_model_wrapper_cls = None
    subject_offstudy_model = None

    @property
    def subject_offstudy_model_cls(self):
        try:
            model_cls = django_apps.get_model(self.subject_offstudy_model)
        except LookupError as e:
            raise SubjectOffstudyViewMixinError(
                f"Unable to lookup subject offstudy model. "
                f"model={self.subject_offstudy_model}. Got {e}"
            )
        return model_cls

    @property
    def subject_offstudy(self):
        """Returns a model instance either saved or unsaved.

        If a save instance does not exits, returns a new unsaved instance.
        """
        model_cls = self.subject_offstudy_model_cls
        try:
            subject_offstudy = model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        except ObjectDoesNotExist:
            subject_offstudy = model_cls(subject_identifier=self.subject_identifier)
        except AttributeError as e:
            if "subject_identifier" in str(e):
                raise SubjectOffstudyViewMixinError(
                    f"Mixin must be declared together with SubjectIdentifierViewMixin. Got {e}"
                )
            raise SubjectOffstudyViewMixinError(e)
        return subject_offstudy
