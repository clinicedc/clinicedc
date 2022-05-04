from typing import Any

from django.apps import apps as django_apps


def get_crf_metadata_model_cls() -> Any:
    return django_apps.get_model("edc_metadata.crfmetadata")


def get_requisition_metadata_model_cls() -> Any:
    return django_apps.get_model("edc_metadata.requisitionmetadata")
