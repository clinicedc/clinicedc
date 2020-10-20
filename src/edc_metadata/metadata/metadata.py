from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_reference import site_reference_configs
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import MISSED_VISIT

from ..constants import NOT_REQUIRED, REQUIRED, KEYED


class CreatesMetadataError(Exception):
    pass


class DeleteMetadataError(Exception):
    pass


class CrfCreator:
    metadata_model = "edc_metadata.crfmetadata"

    def __init__(
        self, visit_model_instance=None, update_keyed=None, crf=None,
    ):
        self._metadata_obj = None
        self.reference_model_cls = None
        self.update_keyed = update_keyed
        self.visit_model_instance = visit_model_instance  # visit model instance
        self.crf = crf

    @property
    def metadata_model_cls(self):
        return django_apps.get_model(self.metadata_model)

    @property
    def options(self):
        options = self.visit_model_instance.metadata_query_options
        options.update(
            {
                "subject_identifier": self.visit_model_instance.subject_identifier,
                "model": self.crf.model,
            }
        )
        return options

    @property
    def metadata_obj(self):
        """Returns a metadata model instance.

        Creates the metadata model instance to represent a
        CRF, if it does not already exist.
        """
        if not self._metadata_obj:
            try:
                metadata_obj = self.metadata_model_cls.objects.get(**self.options)
            except ObjectDoesNotExist:
                metadata_obj = self.metadata_model_cls.objects.create(
                    entry_status=REQUIRED if self.crf.required else NOT_REQUIRED,
                    show_order=self.crf.show_order,
                    site=self.visit_model_instance.site,
                    **self.options,
                )
            else:
                if metadata_obj.entry_status in [REQUIRED, NOT_REQUIRED]:
                    if self.crf.required and metadata_obj.entry_status == NOT_REQUIRED:
                        metadata_obj.entry_status = REQUIRED
                        metadata_obj.save()
                    elif (not self.crf.required) and (
                        metadata_obj.entry_status == REQUIRED
                    ):
                        metadata_obj.entry_status = NOT_REQUIRED
                        metadata_obj.save()
            self._metadata_obj = metadata_obj
        return self._metadata_obj

    def create(self):
        """Creates a metadata model instance to represent a
        CRF, if it does not already exist.
        """
        if self.update_keyed and self.metadata_obj.entry_status != KEYED:
            if self.is_keyed:
                self.metadata_obj.entry_status = KEYED
                self.metadata_obj.save()
        return self.metadata_obj

    @property
    def is_keyed(self):
        """Returns True if CRF is keyed determined by
        querying the reference model.

        See also edc_reference.
        """
        reference_model = site_reference_configs.get_reference_model(
            name=self.crf.model
        )
        self.reference_model_cls = django_apps.get_model(reference_model)
        return self.reference_model_cls.objects.filter_crf_for_visit(
            name=self.crf.model, visit=self.visit_model_instance
        ).exists()


class RequisitionCreator(CrfCreator):
    metadata_model = "edc_metadata.requisitionmetadata"

    def __init__(self, requisition=None, **kwargs):
        super().__init__(crf=requisition, **kwargs)

    @property
    def requisition(self):
        return self.crf

    @property
    def options(self):
        options = super().options
        options.update({"panel_name": self.requisition.panel.name})
        return options

    @property
    def is_keyed(self):
        """Returns True if requisition is keyed determined by
        getting the reference model instance for this
        requisition+panel_name .

        See also edc_reference.
        """
        name = f"{self.requisition.model}.{self.requisition.panel.name}"
        reference_model = site_reference_configs.get_reference_model(name=name)
        self.reference_model_cls = django_apps.get_model(reference_model)
        return self.reference_model_cls.objects.get_requisition_for_visit(
            name=name, visit=self.visit_model_instance
        )


class Creator:
    crf_creator_cls = CrfCreator
    requisition_creator_cls = RequisitionCreator

    def __init__(self, visit_model_instance=None, update_keyed=None):
        self.visit_model_instance = visit_model_instance
        self.update_keyed = update_keyed
        self.visit_code_sequence = visit_model_instance.visit_code_sequence
        self.visit = (
            site_visit_schedules.get_visit_schedule(
                visit_model_instance.visit_schedule_name
            )
            .schedules.get(visit_model_instance.schedule_name)
            .visits.get(visit_model_instance.visit_code)
        )

    @property
    def crfs(self):
        """Returns list of crfs for this visit based on
        values for visit_code_sequence and MISSED_VISIT.
        """
        if self.visit_model_instance.reason == MISSED_VISIT:
            return self.visit.crfs_missed
        elif self.visit_code_sequence != 0:
            return self.visit.crfs_unscheduled
        return self.visit.crfs

    @property
    def requisitions(self):
        if self.visit_code_sequence != 0:
            return self.visit.requisitions_unscheduled
        elif self.visit_model_instance.reason == MISSED_VISIT:
            return ()
        return self.visit.requisitions

    def create(self):
        """Creates metadata for all CRFs and requisitions for
        the scheduled or unscheduled visit instance.
        """
        for crf in self.crfs:
            self.create_crf(crf)
        for requisition in self.requisitions:
            self.create_requisition(requisition)

    def create_crf(self, crf):
        return self.crf_creator_cls(
            crf=crf,
            update_keyed=self.update_keyed,
            visit_model_instance=self.visit_model_instance,
        ).create()

    def create_requisition(self, requisition):
        return self.requisition_creator_cls(
            requisition=requisition,
            update_keyed=self.update_keyed,
            visit_model_instance=self.visit_model_instance,
        ).create()


class Destroyer:
    metadata_crf_model = "edc_metadata.crfmetadata"
    metadata_requisition_model = "edc_metadata.requisitionmetadata"

    def __init__(self, visit_model_instance=None):
        self.visit_model_instance = visit_model_instance

    @property
    def metadata_crf_model_cls(self):
        return django_apps.get_model(self.metadata_crf_model)

    @property
    def metadata_requisition_model_cls(self):
        return django_apps.get_model(self.metadata_requisition_model)

    def delete(self):
        """Deletes all CRF and requisition metadata for
        the visit instance (self.visit_model_instance) excluding where
        entry_status = KEYED.
        """
        qs = self.metadata_crf_model_cls.objects.filter(
            subject_identifier=self.visit_model_instance.subject_identifier,
            **self.visit_model_instance.metadata_query_options,
        ).exclude(entry_status=KEYED)
        deleted = qs.delete()
        qs = self.metadata_requisition_model_cls.objects.filter(
            subject_identifier=self.visit_model_instance.subject_identifier,
            **self.visit_model_instance.metadata_query_options,
        ).exclude(entry_status=KEYED)
        qs.delete()
        return deleted


class Metadata:
    creator_cls = Creator
    destroyer_cls = Destroyer

    def __init__(self, visit_model_instance=None, update_keyed=None):
        app_config = django_apps.get_app_config("edc_metadata")
        self.creator = self.creator_cls(
            visit_model_instance=visit_model_instance, update_keyed=update_keyed
        )
        self.destroyer = self.destroyer_cls(visit_model_instance=visit_model_instance)
        try:
            self.reason_field = app_config.reason_field[
                visit_model_instance._meta.label_lower
            ]
        except KeyError as e:
            raise CreatesMetadataError(
                f"Unable to determine the reason field for model "
                f"{visit_model_instance._meta.label_lower}. Got {e}. "
                f"edc_metadata.AppConfig reason_field = {app_config.reason_field}"
            ) from e
        try:
            self.reason = getattr(visit_model_instance, self.reason_field)
        except AttributeError as e:
            raise CreatesMetadataError(
                f"Invalid reason field. Expected attribute {self.reason_field}. "
                f"{visit_model_instance._meta.label_lower}. Got {e}. "
                f"edc_metadata.AppConfig reason_field = {app_config.reason_field}"
            ) from e
        if not self.reason:
            raise CreatesMetadataError(
                f"Invalid reason from field '{self.reason_field}'. Got None. "
                "Check field value and/or edc_metadata.AppConfig."
                "create_on_reasons/delete_on_reasons."
            )

    def prepare(self):
        """Creates or deletes metadata, depending on the visit reason,
        for the visit instance.
        """
        metadata_exists = False
        app_config = django_apps.get_app_config("edc_metadata")
        if self.reason in app_config.delete_on_reasons:
            self.destroyer.delete()
        elif self.reason in app_config.create_on_reasons:
            self.destroyer.delete()
            self.creator.create()
            metadata_exists = True
        else:
            visit = self.creator.visit
            raise CreatesMetadataError(
                f"Undefined 'reason'. Cannot create metadata. Got "
                f"reason='{self.reason}'. Visit='{visit}'. "
                "Check field value and/or edc_metadata.AppConfig."
                "create_on_reasons/delete_on_reasons."
            )
        return metadata_exists
