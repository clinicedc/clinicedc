from django.apps import apps

from ..models import BaseVisitTracking


class VisitTrackingMixin(object):

    def get_visit_model_app(self):
        """Returns the app that contains the visit model for the
        RARE case where it is not in the same app as this model."""
        return None

    def get_visit_model(self, instance):
        """Returns the visit model which is a subclass of :class:`BaseVisitTracking`."""
        for model in apps.get_models(apps.get_app(instance._meta.app_label)):
            if isinstance(model(), BaseVisitTracking):
                return model
        raise TypeError(
            'Unable to determine the visit model from instance {0} for app {1}'.format(
                instance._meta.object_name, instance._meta.app_label))

    def get_visit_model_cls(self, instance=None):
        """Returns the visit model which is a subclass of :class:`BaseVisitTracking`."""
        if not instance:
            instance = self
        if instance.get_visit_model_app():
            app_label = instance.get_visit_model_app()
        else:
            app_label = instance._meta.app_label
        for model in apps.get_models(apps.get_app(app_label)):
            if isinstance(model(), BaseVisitTracking):
                return model
        raise TypeError(
            'Unable to determine the visit model for app {1} from instance {0}. '
            'Visit model and Off Study model are expected to be in the same app. '
            'If not use model method \'get_visit_model_app()\''.format(
                instance._meta.object_name, instance._meta.app_label))
