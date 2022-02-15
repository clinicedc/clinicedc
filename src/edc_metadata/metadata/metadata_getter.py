from typing import Optional
from warnings import warn

from django.apps import apps as django_apps
from django.contrib.admin.sites import all_sites
from django.core.exceptions import (
    ImproperlyConfigured,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
)
from edc_appointment.stubs import AppointmentModelStub
from edc_visit_tracking.stubs import SubjectVisitModelStub
from edc_visit_tracking.utils import get_subject_visit_model_cls

from edc_metadata import KEYED

from .metadata import model_cls_registered_with_admin_site


class MetadataGetterError(Exception):
    pass


class MetadataValidator:
    def __init__(self, metadata_obj, visit_model_instance):
        self.metadata_obj = metadata_obj
        self.visit_model_instance = visit_model_instance
        self.validate_metadata_object()

    @property
    def extra_query_attrs(self):
        return {}

    def validate_metadata_object(self) -> None:
        if self.metadata_obj:
            # confirm model class exists
            try:
                model_cls = django_apps.get_model(self.metadata_obj.model)
            except LookupError:
                self.metadata_obj.delete()
                self.metadata_obj = None
            else:
                if not model_cls_registered_with_admin_site(model_cls):
                    warn(
                        "Model class not registered with Admin. "
                        f"Deleting related metadata. Got {model_cls}."
                    )
                    # TODO: delete all metadata instances for this model cls?
                    self.metadata_obj.delete()
                    self.metadata_obj = None
                else:
                    # confirm metadata.entry_status is correct
                    model_obj = None
                    query_attrs = {
                        f"{model_cls.visit_model_attr()}": self.visit_model_instance
                    }
                    query_attrs.update(**self.extra_query_attrs)
                    try:
                        model_obj = model_cls.objects.get(**query_attrs)
                    except AttributeError as e:
                        if "visit_model_attr" not in str(e):
                            raise ImproperlyConfigured(f"{e} See {repr(model_cls)}")
                        raise
                        # metadata_obj.delete()
                        # metadata_obj = None
                    except ObjectDoesNotExist:
                        pass
                    except MultipleObjectsReturned:
                        raise
                    self.metadata_obj = self.verify_entry_status_with_model_obj(model_obj)

    def verify_entry_status_with_model_obj(self, model_obj):
        """Verifies that entry_status is set to KEYED if the model
        instance exists, etc.

        Fixes on the fly if model obj exists and entry status != KEYED."""
        # TODO: add test, fixes on the fly
        if model_obj and model_obj.id and self.metadata_obj.entry_status != KEYED:
            msg = (
                "Model instance exists but entry status=="
                f"{self.metadata_obj.entry_status}. See {self.metadata_obj} and "
                f"{model_obj.__class__.__name__}({model_obj}). Fixed."
            )
            warn(msg)
            self.metadata_obj.entry_status = KEYED
            self.metadata_obj.save()
            self.metadata_obj.refresh_from_db()
        # TODO: add test, how can the entry status be reset?
        #  Do we need to recalculate the visit's metadata??
        elif not model_obj and self.metadata_obj.entry_status == KEYED:
            msg = (
                "Model instance does not exist but entry status == "
                f"{self.metadata_obj.entry_status}. See {self.metadata_obj}"
            )
            raise MetadataGetterError(msg)

    @staticmethod
    def model_cls_registered_with_admin_site(model_cls) -> bool:
        """Returns True if model cls is registered in Admin."""
        for admin_site in all_sites:
            if model_cls in admin_site._registry:
                return True
        return False


class MetadataGetter:

    """A class that gets a filtered queryset of metadata --
    `metadata_objects`.
    """

    metadata_model: Optional[str] = None

    metadata_validator_cls = MetadataValidator

    def __init__(
        self,
        appointment: Optional[AppointmentModelStub] = None,
        subject_identifier: Optional[str] = None,
        visit_code: Optional[str] = None,
        visit_code_sequence: Optional[int] = None,
    ) -> None:
        self.options = {}
        self.visit_model_instance: Optional[SubjectVisitModelStub] = None
        try:
            self.visit_model_instance = appointment.visit  # type:ignore
        except AttributeError:
            self.subject_identifier = subject_identifier
            self.visit_code = visit_code
            self.visit_code_sequence = visit_code_sequence
            try:
                self.visit_model_instance = get_subject_visit_model_cls().objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_code=self.visit_code,
                    visit_code_sequence=self.visit_code_sequence,
                )
            except ObjectDoesNotExist as e:
                raise MetadataGetterError(f"Unable to find visit model instance. Got {e}")
        else:
            self.subject_identifier = self.visit_model_instance.subject_identifier
            self.visit_code = self.visit_model_instance.visit_code
            self.visit_code_sequence = self.visit_model_instance.visit_code_sequence
        query_options = dict(
            subject_identifier=self.subject_identifier,
            visit_code=self.visit_code,
            visit_code_sequence=self.visit_code_sequence,
        )
        self.validate_metadata_objects(query_options)
        self.metadata_objects = self.metadata_model_cls.objects.filter(
            **query_options
        ).order_by("show_order")

    @property
    def metadata_model_cls(self):
        return django_apps.get_model(self.metadata_model)

    def next_object(self, show_order=None, entry_status=None):
        """Returns the next model instance based on the show order."""
        if show_order is None:
            metadata_obj = None
        else:
            opts = {"show_order__gt": show_order}
            if entry_status:
                opts.update(entry_status=entry_status)
            metadata_obj = self.metadata_objects.filter(**opts).order_by("show_order").first()
        return metadata_obj

    def validate_metadata_objects(self, query_options) -> None:
        qs = self.metadata_model_cls.objects.filter(**query_options)
        for metadata_obj in qs:
            self.metadata_validator_cls(metadata_obj, self.visit_model_instance)
            # validate_metadata_object(metadata_obj, visit=self.visit_model_instance)
