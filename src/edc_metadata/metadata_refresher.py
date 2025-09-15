from __future__ import annotations

import sys
from typing import Any

from django.apps import apps as django_apps
from django.contrib.admin.sites import all_sites
from django.db.models import Count
from tqdm import tqdm

from edc_appointment.models import Appointment
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.utils import get_related_visit_model_cls

from .metadata import CrfMetadataGetter, RequisitionMetadataGetter
from .metadata_rules import site_metadata_rules


class MetadataRefresher:
    """A class to be `run` when metadata gets out-of-date

    This may happen when there are changes to the visit schedule,
    metadata rules or manual changes to data.
    """

    def __init__(self, verbose: bool | None = None):
        self._source_models = []
        self._admin_models = []
        self.verbose = verbose

    def run(self) -> None:
        self._message("Updating metadata ...     \n")
        self.create_or_update_metadata_for_all()

        # note: only need to run metadata rules on the related
        # visit model
        self._message("Running metadata rules ...\n")
        total = get_related_visit_model_cls().objects.all().count()
        self.run_metadata_rules(get_related_visit_model_cls(), total)
        self._message("Done.\n")

    @property
    def source_models(self) -> list[str]:
        if not self._source_models:
            self._source_models = []
            for app_label, rule_groups_list in site_metadata_rules.rule_groups.items():
                for rule_groups in rule_groups_list:
                    if (
                        rule_groups._meta.source_model
                        != get_related_visit_model_cls()._meta.label_lower
                    ):
                        self._source_models.append(rule_groups._meta.source_model)
            self._source_models = list(set(self._source_models))
            self._source_models.sort()
            self._source_models.insert(0, get_related_visit_model_cls()._meta.label_lower)
            self._message(f"  Found source models: {', '.join(self.source_models)}.\n")
        return self._source_models

    @staticmethod
    def run_metadata_rules(source_model_cls: Any, total: int) -> None:
        """Updates rules for all instances of this source model"""
        for instance in tqdm(source_model_cls.objects.all(), total=total):
            if django_apps.get_app_config("edc_metadata").metadata_rules_enabled:
                instance.run_metadata_rules()

    def create_or_update_metadata(self, source_model_cls: Any, total: int) -> None:
        """Creates or updates CRF/Requisition metadata for all instances
        of this source model.
        """
        for instance in tqdm(source_model_cls.objects.all(), total=total):
            try:
                instance.metadata_create()
            except AttributeError:
                try:
                    instance.metadata_update()
                except AttributeError as e:
                    self._message(f"      skipping (got {e})     \n")
                    break

    def _message(self, msg: str) -> None:
        if self.verbose:
            sys.stdout.write(msg)

    @property
    def crf_metadata_models(self) -> list[CrfMetadata]:
        return [
            obj.get("model")
            for obj in CrfMetadata.objects.values("model")
            .order_by("model")
            .annotate(count=Count("model"))
        ]

    @property
    def requisition_metadata_models(self) -> list[RequisitionMetadata]:
        return [
            obj.get("model")
            for obj in RequisitionMetadata.objects.values("model")
            .order_by("model")
            .annotate(count=Count("model"))
        ]

    @property
    def admin_models(self) -> list:
        if not self._admin_models:
            for admin_site in all_sites:
                self._admin_models.extend(
                    [cls._meta.label_lower for cls in admin_site._registry]
                )
        return self._admin_models

    def verifying_crf_metadata_with_visit_schedule_and_admin(self) -> None:
        self._message("- Verifying CrfMetadata models with visit schedule and admin.\n")
        for model in self.crf_metadata_models:
            if (
                model not in site_visit_schedules.all_post_consent_models
                and model not in self.admin_models
            ):
                count = CrfMetadata.objects.filter(model=model).delete()
                self._message(f"   * deleted {count} metadata records for model {model}.\n")
        self._message("    Done.\n")

    def verifying_requisition_metadata_with_visit_schedule_and_admin(self) -> None:
        self._message(
            "- Verifying RequisitionMetadata models with visit schedule and admin.\n"
        )
        for model in self.requisition_metadata_models:
            if (
                model not in site_visit_schedules.all_post_consent_models
                and model not in self.admin_models
            ):
                count = RequisitionMetadata.objects.filter(model=model).delete()
                self._message(f"   * deleted {count} metadata records for model {model}.\n")
        self._message("    Done.\n")

    def create_or_update_metadata_for_all(self) -> None:
        self.verifying_crf_metadata_with_visit_schedule_and_admin()
        self.verifying_requisition_metadata_with_visit_schedule_and_admin()
        # TODO: perhaps always delete before running
        self._message("- Updating metadata for all post consent models...     \n")
        models = dict(sorted(site_visit_schedules.all_post_consent_models.items()))
        model_count = len(list(models))
        related_visits = get_related_visit_model_cls().objects.all()
        total = related_visits.count()
        self._message(
            f"   - {model_count} post-consent models found for {total} visits ... \n"
        )
        for related_visit in tqdm(related_visits, total=total):
            related_visit.metadata_create()
        self._message("    Done.\n")

    def validate_metadata_for_all(self):
        self._message("- Validating all metadata ...     \n")
        appointments = Appointment.objects.all().order_by("site_id")
        total = appointments.count()
        for appointment in tqdm(appointments, total=total):
            CrfMetadataGetter(appointment=appointment)
            RequisitionMetadataGetter(appointment=appointment)
