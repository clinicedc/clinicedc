from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_reference import site_reference_configs
from edc_visit_schedule import site_visit_schedules

from ..constants import NOT_REQUIRED, REQUIRED, KEYED


class CreatesMetadataError(Exception):
    pass


class DeleteMetadataError(Exception):
    pass


class Base:
    def __init__(
        self,
        visit=None,
        metadata_crf_model=None,
        metadata_requisition_model=None,
        **kwargs,
    ):
        self.reference_model_cls = None
        app_config = django_apps.get_app_config("edc_metadata")
        self.visit = visit  # visit model instance
        self.metadata_crf_model = metadata_crf_model or app_config.crf_model_cls
        self.metadata_requisition_model = (
            metadata_requisition_model or app_config.metadata_requisition_model_cls
        )


class CrfCreator(Base):
    def __init__(self, visit=None, update_keyed=None, **kwargs):
        super().__init__(visit=visit, **kwargs)
        self.update_keyed = update_keyed

    def create(self, crf=None):
        """Creates a metadata model instance to represent a
        CRF, if it does not already exist.
        """
        options = self.visit.metadata_query_options
        options.update(
            {"subject_identifier": self.visit.subject_identifier, "model": crf.model}
        )
        try:
            metadata_obj = self.metadata_crf_model.objects.get(**options)
        except ObjectDoesNotExist:
            metadata_obj = self.metadata_crf_model.objects.create(
                entry_status=REQUIRED if crf.required else NOT_REQUIRED,
                show_order=crf.show_order,
                **options,
            )
        if self.update_keyed and metadata_obj.entry_status != KEYED:
            if self.is_keyed(crf):
                metadata_obj.entry_status = KEYED
                metadata_obj.save()

    def is_keyed(self, crf=None):
        """Returns True if CRF is keyed determined by
        querying the reference model.

        See also edc_reference.
        """
        reference_model = site_reference_configs.get_reference_model(name=crf.model)
        self.reference_model_cls = django_apps.get_model(reference_model)
        return self.reference_model_cls.objects.filter_crf_for_visit(
            name=crf.model, visit=self.visit
        ).exists()


class RequisitionCreator(Base):
    def __init__(self, visit=None, update_keyed=None, **kwargs):
        super().__init__(visit=visit, **kwargs)
        self.update_keyed = update_keyed

    def create(self, requisition=None):
        """Creates a metadata models instance to represent
        a requisition, if it does not already exist.
        """
        options = self.visit.metadata_query_options
        options.update(
            {
                "subject_identifier": self.visit.subject_identifier,
                "model": requisition.model,
                "panel_name": requisition.panel.name,
            }
        )
        try:
            metadata_obj = self.metadata_requisition_model.objects.get(**options)
        except ObjectDoesNotExist:
            metadata_obj = self.metadata_requisition_model.objects.create(
                entry_status=REQUIRED if requisition.required else NOT_REQUIRED,
                show_order=requisition.show_order,
                **options,
            )
        if (
            self.update_keyed
            and metadata_obj.entry_status != KEYED
            and self.is_keyed(requisition)
        ):
            metadata_obj.entry_status = KEYED
            metadata_obj.save()
        return metadata_obj

    def is_keyed(self, requisition=None):
        """Returns True if requisition is keyed determined by
        getting the reference model instance for this
        requisition+panel_name .

        See also edc_reference.
        """
        name = f"{requisition.model}.{requisition.panel.name}"
        reference_model = site_reference_configs.get_reference_model(name=name)
        self.reference_model_cls = django_apps.get_model(reference_model)
        return self.reference_model_cls.objects.get_requisition_for_visit(
            name=name, visit=self.visit
        )


class Creator:

    crf_creator_cls = CrfCreator
    requisition_creator_cls = RequisitionCreator

    def __init__(self, visit=None, **kwargs):
        """param `visit` is the visit model instance --
        `instance` is not.
        """
        self.crf_creator = self.crf_creator_cls(visit=visit, **kwargs)
        self.requisition_creator = self.requisition_creator_cls(visit=visit, **kwargs)
        self.visit_code_sequence = visit.visit_code_sequence
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit.visit_schedule_name
        )
        schedule = visit_schedule.schedules.get(visit.schedule_name)
        self.visit = schedule.visits.get(visit.visit_code)

    @property
    def crfs(self):
        if self.visit_code_sequence != 0:
            return self.visit.crfs_unscheduled
        return self.visit.crfs

    @property
    def requisitions(self):
        if self.visit_code_sequence != 0:
            return self.visit.requisitions_unscheduled
        return self.visit.requisitions

    def create(self):
        """Creates metadata for all CRFs and requisitions for
        the scheduled or unscheduled visit instance.
        """
        for crf in self.crfs:
            self.create_crf(crf=crf)
        for requisition in self.requisitions:
            self.create_requisition(requisition=requisition)

    def create_crf(self, crf=None):
        return self.crf_creator.create(crf=crf)

    def create_requisition(self, requisition=None):
        return self.requisition_creator.create(requisition=requisition)


class Destroyer(Base):
    def delete(self):
        """Deletes all CRF and requisition metadata for
        the visit instance (self.visit) excluding where
        entry_status = KEYED.
        """
        deleted = (
            self.metadata_crf_model.objects.filter(
                subject_identifier=self.visit.subject_identifier,
                **self.visit.metadata_query_options,
            )
            .exclude(entry_status=KEYED)
            .delete()
        )
        self.metadata_requisition_model.objects.filter(
            subject_identifier=self.visit.subject_identifier,
            **self.visit.metadata_query_options,
        ).exclude(entry_status=KEYED).delete()
        return deleted


class Metadata:

    creator_cls = Creator
    destroyer_cls = Destroyer

    def __init__(self, visit=None, update_keyed=None, **kwargs):
        app_config = django_apps.get_app_config("edc_metadata")
        self.creator = self.creator_cls(
            visit=visit, update_keyed=update_keyed, **kwargs
        )
        self.destroyer = self.destroyer_cls(visit=visit, **kwargs)
        try:
            self.reason_field = app_config.reason_field[visit._meta.label_lower]
        except KeyError as e:
            raise CreatesMetadataError(
                f"Unable to determine the reason field for model "
                f"{visit._meta.label_lower}. Got {e}. "
                f"edc_metadata.AppConfig reason_field = {app_config.reason_field}"
            ) from e
        try:
            self.reason = getattr(visit, self.reason_field)
        except AttributeError as e:
            raise CreatesMetadataError(
                f"Invalid reason field. Expected attribute {self.reason_field}. "
                f"{visit._meta.label_lower}. Got {e}. "
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
