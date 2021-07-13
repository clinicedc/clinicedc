from django.core.exceptions import ImproperlyConfigured
from django.db import models

from .utils import get_diagnosis_labels


class DiagnosisModelMixin(models.Model):

    diagnoses_labels = get_diagnosis_labels()

    @property
    def diagnoses(self) -> dict:
        if not self.diagnoses_labels:
            raise ImproperlyConfigured("Settings attribute EDC_DIAGNOSIS_LABELS not set.")
        return {k: getattr(self, f"{k}_dx") for k in self.diagnoses_labels}

    class Meta:
        abstract = True
