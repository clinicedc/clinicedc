from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.contrib.admin.sites import all_sites
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction

from edc_visit_schedule.visit import CrfCollection, RequisitionCollection
from edc_visit_tracking.constants import MISSED_VISIT

from ..constants import KEYED, NOT_REQUIRED, REQUIRED
from ..metadata_mixins import SourceModelMetadataMixin
from ..utils import verify_model_cls_registered_with_admin

if TYPE_CHECKING:
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin
    from edc_visit_schedule.visit import Crf, Requisition
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ..model_mixins.creates import CreatesMetadataModelMixin
    from ..models import CrfMetadata, RequisitionMetadata

    class RelatedVisitModel(SiteModelMixin, CreatesMetadataModelMixin, Base, BaseUuidModel):
        pass


class CreatesMetadataError(Exception):
    pass


class DeleteMetadataError(Exception):
    pass


def model_cls_registered_with_admin_site(model_cls: Any) -> bool:
    """Returns True if model cls is registered in Admin.

    See also settings.EDC_METADATA_VERIFY_MODELS_REGISTERED_WITH_ADMIN
    """
    registered = False
    if not verify_model_cls_registered_with_admin():
        registered = True
    else:
        for admin_site in all_sites:
            if model_cls in admin_site._registry:
                registered = True
    return registered


class CrfCreator(SourceModelMetadataMixin):
    metadata_model: str = "edc_metadata.crfmetadata"

    def __init__(
        self,
        related_visit: RelatedVisitModel,
        update_keyed: bool,
        crf: Crf | Requisition,
    ) -> None:
        super().__init__(source_model=crf.model, related_visit=related_visit)
        self._metadata_obj = None
        self.update_keyed = update_keyed
        self.crf = crf

    @property
    def metadata_model_cls(
        self,
    ) -> CrfMetadata | RequisitionMetadata:
        return django_apps.get_model(self.metadata_model)

    @property
    def query_options(self) -> dict:
        query_options = self.related_visit.metadata_query_options
        query_options.update(
            {
                "subject_identifier": self.related_visit.subject_identifier,
                "model": self.source_model,
            }
        )
        return query_options

    @property
    def metadata_obj(self) -> CrfMetadata | RequisitionMetadata | None:
        """Gets or creates a metadata model instance.

        If the source model is not registered in an admin_site, deletes
        the metadata_obj, if it exists, and returns None.
        """
        if not self._metadata_obj:
            metadata_obj = None
            registered = model_cls_registered_with_admin_site(self.source_model_cls)
            try:
                metadata_obj = self.metadata_model_cls.objects.get(**self.query_options)
            except ObjectDoesNotExist:
                if registered:
                    with transaction.atomic():
                        opts = dict(
                            entry_status=(REQUIRED if self.crf.required else NOT_REQUIRED),
                            show_order=self.crf.show_order,
                            site=self.related_visit.site,
                            due_datetime=self.due_datetime,
                            fill_datetime=self.fill_datetime,
                            document_user=self.document_user,
                            document_name=self.document_name,
                        )
                        opts.update(**self.query_options)
                        try:
                            metadata_obj = self.metadata_model_cls.objects.create(**opts)
                        except IntegrityError as e:
                            msg = f"Integrity error creating. Tried with {opts}. Got {e}."
                            raise CreatesMetadataError(msg) from e
            else:
                if not registered:
                    metadata_obj.delete()
                    metadata_obj = None
            if metadata_obj:
                metadata_obj = self.update_entry_status_to_default_or_keyed(metadata_obj)
            self._metadata_obj = metadata_obj
        return self._metadata_obj

    def create(self) -> CrfMetadata | RequisitionMetadata:
        """Creates a metadata model instance to represent a
        CRF, if it does not already exist (get_or_create).
        """
        return self.metadata_obj

    def update_entry_status_to_default_or_keyed(
        self, metadata_obj: CrfMetadata | RequisitionMetadata
    ):
        """Sets the `entry_status` to the default unless source model
         already exists.

        If the source model instance already exists (is_keyed),
        `entry_status` will set to KEYED.

        Note: that the default `entry_status` may be changed by rules
        later on.
        """
        if metadata_obj.entry_status != KEYED and self.source_model_obj_exists:
            metadata_obj.entry_status = KEYED
            metadata_obj.save(update_fields=["entry_status"])
            metadata_obj.refresh_from_db()
        elif metadata_obj.entry_status in [REQUIRED, NOT_REQUIRED]:
            if self.crf.required and metadata_obj.entry_status == NOT_REQUIRED:
                metadata_obj.entry_status = REQUIRED
                metadata_obj.save(update_fields=["entry_status"])
                metadata_obj.refresh_from_db()
            elif (not self.crf.required) and (metadata_obj.entry_status == REQUIRED):
                metadata_obj.entry_status = NOT_REQUIRED
                metadata_obj.save(update_fields=["entry_status"])
                metadata_obj.refresh_from_db()
        return metadata_obj


class RequisitionCreator(CrfCreator):
    metadata_model: str = "edc_metadata.requisitionmetadata"

    def __init__(
        self,
        requisition: Requisition,
        update_keyed: bool,
        related_visit: RelatedVisitModel,
    ) -> None:
        super().__init__(
            crf=requisition,
            update_keyed=update_keyed,
            related_visit=related_visit,
        )
        self.panel_name: str = f"{self.requisition.model}.{self.requisition.panel.name}"

    @property
    def requisition(self) -> Requisition:
        return self.crf

    @property
    def query_options(self) -> dict:
        query_options = super().query_options
        query_options.update({"panel_name": self.requisition.panel.name})
        return query_options

    @property
    def source_model_options(self) -> dict:
        """Source model query options"""
        return dict(subject_visit=self.related_visit, panel__name=self.requisition.panel.name)


class Creator:
    crf_creator_cls = CrfCreator
    requisition_creator_cls = RequisitionCreator

    def __init__(
        self,
        update_keyed: bool,
        related_visit: RelatedVisitModel,
    ) -> None:
        self.related_visit = related_visit
        self.update_keyed = update_keyed

    @property
    def crfs(self) -> CrfCollection:
        """Returns list of crfs for this visit based on
        values for visit_code_sequence and MISSED_VISIT.
        """
        if self.related_visit.reason == MISSED_VISIT:
            # missed visit CRFs only
            crfs = self.related_visit.visit.crfs_missed.forms
        elif self.related_visit.visit_code_sequence != 0:
            # unscheduled + prn CRFs only
            models = [crf.model for crf in self.related_visit.visit.crfs_unscheduled]
            crfs = self.related_visit.visit.crfs_unscheduled.forms + tuple(
                [f for f in self.related_visit.visit.crfs_prn if f.model not in models]
            )
        else:
            # scheduled + prn CRFs only
            models = [crf.model for crf in self.related_visit.visit.crfs]
            crfs = self.related_visit.visit.crfs.forms + tuple(
                [f for f in self.related_visit.visit.crfs_prn if f.model not in models]
            )
        return CrfCollection(*crfs, name="crfs")

    @property
    def requisitions(self) -> RequisitionCollection:
        if self.related_visit.visit_code_sequence != 0:
            # unscheduled + prn requisitions only
            names = [f.name for f in self.related_visit.visit.requisitions_unscheduled]
            requisitions = self.related_visit.visit.requisitions_unscheduled.forms + tuple(
                [f for f in self.related_visit.visit.requisitions_prn if f.name not in names]
            )
        elif self.related_visit.reason == MISSED_VISIT:
            # missed visit requisition only -- none
            requisitions = ()
        else:
            # scheduled + prn requisitions only
            names = [f.name for f in self.related_visit.visit.requisitions]
            requisitions = self.related_visit.visit.requisitions.forms + tuple(
                [f for f in self.related_visit.visit.requisitions_prn if f.name not in names]
            )
        return RequisitionCollection(*requisitions, name="requisitions")

    def create(self) -> None:
        """Creates metadata for all CRFs and requisitions for
        the scheduled or unscheduled visit instance.
        """
        for crf in self.crfs:
            self.create_crf(crf)
        for requisition in self.requisitions:
            self.create_requisition(requisition)

    def create_crf(self, crf) -> CrfMetadata:
        return self.crf_creator_cls(
            crf=crf,
            update_keyed=self.update_keyed,
            related_visit=self.related_visit,
        ).create()

    def create_requisition(self, requisition) -> RequisitionMetadata:
        return self.requisition_creator_cls(
            requisition=requisition,
            update_keyed=self.update_keyed,
            related_visit=self.related_visit,
        ).create()


class Destroyer:
    metadata_crf_model = "edc_metadata.crfmetadata"
    metadata_requisition_model = "edc_metadata.requisitionmetadata"

    def __init__(self, related_visit: RelatedVisitModel | CreatesMetadataModelMixin) -> None:
        self.related_visit = related_visit

    @property
    def metadata_crf_model_cls(self) -> CrfMetadata:
        return django_apps.get_model(self.metadata_crf_model)

    @property
    def metadata_requisition_model_cls(self) -> RequisitionMetadata:
        return django_apps.get_model(self.metadata_requisition_model)

    def delete(self, entry_status_not_in: list[str] = None) -> int:
        """Deletes all CRF and requisition metadata for the
        related_visit instance excluding where entry_status in
        [KEYED, NOT_REQUIRED].
        """
        entry_status = entry_status_not_in or [KEYED, NOT_REQUIRED]
        qs = self.metadata_crf_model_cls.objects.filter(
            subject_identifier=self.related_visit.subject_identifier,
            **self.related_visit.metadata_query_options,
        ).exclude(entry_status__in=entry_status)
        deleted = qs.delete()
        qs = self.metadata_requisition_model_cls.objects.filter(
            subject_identifier=self.related_visit.subject_identifier,
            **self.related_visit.metadata_query_options,
        ).exclude(entry_status__in=entry_status)
        qs.delete()
        return deleted


class Metadata:
    creator_cls = Creator
    destroyer_cls = Destroyer

    def __init__(
        self,
        related_visit: RelatedVisitModel | CreatesMetadataModelMixin,
        update_keyed: bool,
    ) -> None:
        self._reason = None
        self._reason_field = "reason"
        self.related_visit = related_visit
        self.creator = self.creator_cls(related_visit=related_visit, update_keyed=update_keyed)
        self.destroyer = self.destroyer_cls(related_visit=related_visit)

    def prepare(self) -> bool:
        """Creates and deletes, or just deletes, metadata, depending
        on the related_visit `reason`.
        """
        metadata_exists = False
        if self.reason in self.related_visit.visit_schedule.delete_metadata_on_reasons:
            self.destroyer.delete()
        elif self.reason in self.related_visit.visit_schedule.create_metadata_on_reasons:
            if self.reason == MISSED_VISIT:
                self.destroyer.delete(entry_status_not_in=[KEYED])
            else:
                self.destroyer.delete(entry_status_not_in=[KEYED, NOT_REQUIRED])
            self.creator.create()
            metadata_exists = True
        else:
            raise CreatesMetadataError(
                f"Undefined 'reason'. Cannot create metadata. Got "
                f"reason='{self.reason}'. Visit='{self.related_visit.visit}'. "
                "Check field value and/or edc_metadata.AppConfig."
                "create_on_reasons/delete_on_reasons."
            )
        return metadata_exists

    @property
    def reason(self):
        """Returns the `value` of the reason field on the
        related_visit model instance.

        For example: `schedule` or `unscheduled`
        """
        if not self._reason:
            reason_field = self.related_visit.visit_schedule.visit_model_reason_field
            try:
                self._reason = getattr(self.related_visit, reason_field)
            except AttributeError as e:
                raise CreatesMetadataError(
                    f"Invalid reason field. Expected attribute {reason_field}. "
                    f"{self.related_visit._meta.label_lower}. Got {e}. "
                    f"visit schedule `{self.related_visit.visit_schedule.name}` "
                    f"visit_model_reason_field = {reason_field}"
                ) from e
            if not self._reason:
                raise CreatesMetadataError(
                    f"Invalid reason from field '{reason_field}'. Got None. "
                    "Check field value and/or edc_metadata.AppConfig."
                    "create_on_reasons/delete_on_reasons."
                )
        return self._reason
