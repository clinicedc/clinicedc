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

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         if not self.offstudy_model_wrapper_cls:
#             raise SubjectOffstudyViewMixinError(
#                 'subject_offstudy_model_wrapper_cls must be a valid ModelWrapper. Got None')
#         if not self.subject_offstudy_model:
#             raise SubjectOffstudyViewMixinError(
#                 'subject_offstudy_model must be a model (label_lower). Got None')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         wrapper = self.offstudy_model_wrapper_cls(
#             model_obj=self.subject_offstudy)
#         context.update(subject_offstudy=wrapper)
#         return context

    @property
    def subject_offstudy_model_cls(self):
        try:
            model_cls = django_apps.get_model(self.subject_offstudy_model)
        except LookupError as e:
            raise SubjectOffstudyViewMixinError(
                f'Unable to lookup subject offstudy model. '
                f'model={self.subject_offstudy_model}. Got {e}')
        return model_cls

    @property
    def subject_offstudy(self):
        """Returns a model instance either saved or unsaved.

        If a save instance does not exits, returns a new unsaved instance.
        """
        model_cls = self.subject_offstudy_model_cls
        try:
            subject_offstudy = model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            subject_offstudy = model_cls(
                subject_identifier=self.subject_identifier)
        except AttributeError as e:
            if 'subject_identifier' in str(e):
                raise SubjectOffstudyViewMixinError(
                    f'Mixin must be declared together with SubjectIdentifierViewMixin. Got {e}')
            raise SubjectOffstudyViewMixinError(e)
        return subject_offstudy
