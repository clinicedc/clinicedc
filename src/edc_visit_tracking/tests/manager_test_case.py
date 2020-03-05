from django.apps import apps as django_apps
from edc_appointment.managers import AppointmentManager
from edc_appointment.model_mixins import AppointmentModelMixin
from edc_list_data.model_mixins import ListModelMixin, ListModelManager
from edc_model.models import HistoricalRecords

from ..managers import CrfModelManager, VisitModelManager
from ..model_mixins import VisitModelMixin
from ..model_mixins import VisitTrackingCrfModelMixin


class ManagerTestCase:
    app_label = None

    appointment_manager_cls = AppointmentManager
    appointment_model_cls = AppointmentModelMixin
    crf_manager_cls = CrfModelManager
    crf_model_cls = VisitTrackingCrfModelMixin
    history_manager_cls = HistoricalRecords
    list_manager_cls = ListModelManager
    list_model_cls = ListModelMixin
    visit_manager_cls = VisitModelManager
    visit_model_cls = VisitModelMixin
    requisition_manager_cls = VisitModelManager
    requisition_model_cls = VisitModelMixin

    @property
    def appointment_model(self):
        """Returns the appointment model name.
        """
        appointment_model = None
        app_config = django_apps.get_app_config(self.app_label)
        for model in app_config.get_models():
            if issubclass(model, (self.appointment_model_cls,)):
                appointment_model = model._meta.label_lower
                break
        return appointment_model

    @property
    def visit_models(self):
        """Returns a list of "Visit" model names.
        """
        visit_models = []
        app_config = django_apps.get_app_config(self.app_label)
        for model in app_config.get_models():
            if issubclass(model, (self.visit_model_cls,)):
                visit_models.append(model._meta.label_lower)
        return visit_models

    @property
    def requisition_models(self):
        """Returns a list of "Requisition" model names.
        """
        requisition_models = []
        app_config = django_apps.get_app_config(self.app_label)
        for model in app_config.get_models():
            if issubclass(model, (self.requisition_model_cls,)):
                requisition_models.append(model._meta.label_lower)
        return requisition_models

    @property
    def list_models(self):
        """Returns a list of "List" model names.
        """
        list_models = []
        app_config = django_apps.get_app_config(self.app_label)
        for model in app_config.get_models():
            if issubclass(model, (self.list_model_cls,)):
                list_models.append(model._meta.label_lower)
        return list_models

    @property
    def non_crf_models(self):
        """Returns a list of non-CRF model names.

        Note: A non-crf model is does not include appointment,
        visit, or list models.
        """
        non_crf_models = []
        app_config = django_apps.get_app_config(self.app_label)
        for model in app_config.get_models():
            classes = (
                self.crf_model_cls,
                self.list_model_cls,
                self.appointment_model_cls,
                self.visit_manager_cls,
            )
            if not issubclass(model, classes):
                non_crf_models.append(model._meta.label_lower)
        return non_crf_models

    @property
    def crf_models(self):
        """Returns a list of CRF model names.
        """
        crf_models = []
        app_config = django_apps.get_app_config(self.app_label)
        for model in app_config.get_models():
            if issubclass(model, (self.crf_model_cls,)) and not issubclass(
                model, (self.requisition_model_cls,)
            ):
                crf_models.append(model._meta.label_lower)
        return crf_models

    def have_manager_or_raise(self, models=None, manager_cls=None):
        app_config = django_apps.get_app_config(self.app_label)
        for model in app_config.get_models():
            if model._meta.label_lower in models:
                if (
                    model._default_manager.__class__ != manager_cls
                    and "historical" not in model._meta.label_lower
                ):
                    self.assertTrue(
                        issubclass(model._default_manager.__class__, manager_cls),
                        msg=(
                            f"model {model._meta.label_lower}. "
                            f"Got manager {model._default_manager.__class__} "
                            f"is not a subclass of {manager_cls}."
                        ),
                    )

    def have_history_or_raise(self, models=None):
        app_config = django_apps.get_app_config(self.app_label)
        for model in app_config.get_models():
            if model._meta.label_lower in models:
                if "historical" not in model._meta.label_lower:
                    self.assertTrue(
                        issubclass(model.history.__class__, self.history_manager_cls),
                        msg=(
                            f"model {model._meta.label_lower}. "
                            f"Got history manager {model.history.__class__} "
                            f"is not a subclass of {self.history_manager_cls}."
                        ),
                    )

    def test_crf_default_manager_subclass(self):
        self.have_manager_or_raise(
            models=self.crf_models, manager_cls=self.crf_manager_cls
        )

    def test_crf_history_manager_subclass(self):
        self.have_history_or_raise(models=self.crf_models)

    def test_requisition_default_manager_subclass(self):
        self.have_manager_or_raise(
            models=self.requisition_models, manager_cls=self.requisition_manager_cls
        )

    def test_requisition_history_manager_subclass(self):
        self.have_history_or_raise(models=self.requisition_models)
