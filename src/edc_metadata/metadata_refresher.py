import sys
from typing import Any, Optional

from django.apps import apps as django_apps
from django.contrib.admin.sites import all_sites
from django.db.models import Count
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.utils import get_subject_visit_model_cls
from tqdm import tqdm

from edc_metadata import InvalidTargetPanel, TargetModelNotScheduledForVisit
from edc_metadata.models import CrfMetadata, RequisitionMetadata

from .metadata_rules import site_metadata_rules


class MetadataRefresher:
    """A class to be `run` when metadata gets out-of-date

    This may happen when there are changes to the visit schedule,
    metada rules or manual changes to data.
    """

    def __init__(self, verbose: Optional[bool] = None):
        self._source_models = []
        self.verbose = verbose

    def run(self) -> None:
        self._message("Updating references, updating metadata ...\n")
        for index, source_model in enumerate(self.source_models):
            self._message(f"  {index + 1}. {source_model}\n")
            source_model_cls = django_apps.get_model(source_model)
            total = source_model_cls.objects.all().count()
            self.update_references(source_model_cls, total)
            self._message("    - Updating metadata ...     \n")
            self.create_or_update_metadata(source_model_cls, total)
        total = get_subject_visit_model_cls().objects.all().count()
        self._message("Running metadata rules ...\n")
        self.run_metadata_rules(get_subject_visit_model_cls(), total)
        self._message("Done.\n")

    @property
    def source_models(self) -> list:
        if not self._source_models:
            self._source_models = [get_subject_visit_model_cls()._meta.label_lower]
            for app_label, rule_groups_list in site_metadata_rules.rule_groups.items():
                for rule_groups in rule_groups_list:
                    self._source_models.append(rule_groups._meta.source_model)
            self._source_models = list(set(self._source_models))
            self._message(f"  Found source models: {', '.join(self.source_models)}.\n")
        return self._source_models

    def update_references(self, source_model_cls: Any, total: int) -> None:
        """Updates references for all instances of this source model"""
        self._message("    - Updating references ...\n")
        for instance in tqdm(source_model_cls.objects.all(), total=total):
            instance.update_reference_on_save()

    def run_metadata_rules(self, source_model_cls: Any, total: int) -> None:
        """Updates rules for all instances of this source model"""
        self._message("    - Running rules ...     \n")
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
                except (
                    AttributeError,
                    TargetModelNotScheduledForVisit,
                    InvalidTargetPanel,
                ) as e:
                    self._message(f"      skipping (got {e})     \n")
                    break

    def create_or_update_metadata_for_all(self) -> None:
        admin_models = []
        for admin_site in all_sites:
            admin_models.extend([cls._meta.label_lower for cls in admin_site._registry])
        crf_metadata_models = [
            obj.get("model")
            for obj in CrfMetadata.objects.values("model")
            .order_by("model")
            .annotate(count=Count("model"))
        ]
        requisition_metadata_models = [
            obj.get("model")
            for obj in RequisitionMetadata.objects.values("model")
            .order_by("model")
            .annotate(count=Count("model"))
        ]
        self._message("    - Verifying CrfMetadata models with visit schedule and admin.\n")
        for model in crf_metadata_models:
            if (
                model not in site_visit_schedules.all_post_consent_models
                and model not in admin_models
            ):
                count = CrfMetadata.objects.filter(model=model).delete()
                self._message(f"      * deleted {count} metadata records for model {model}.\n")
        self._message(
            "    - Verifying RequisitionMetadata models with visit schedule and admin.\n"
        )
        for model in requisition_metadata_models:
            if (
                model not in site_visit_schedules.all_post_consent_models
                and model not in admin_models
            ):
                count = RequisitionMetadata.objects.filter(model=model).delete()
                self._message(f"      * deleted {count} metadata records for model {model}.\n")

        self._message("    - Updating metadata ...     \n")
        for model in site_visit_schedules.all_post_consent_models:
            model_cls = django_apps.get_model(model)
            total = model_cls.objects.all().count()
            self._message(f"      * {model_cls._meta.label_lower} ...     \n")
            self.create_or_update_metadata(model_cls, total)

    def _message(self, msg: str) -> None:
        if self.verbose:
            sys.stdout.write(msg)
