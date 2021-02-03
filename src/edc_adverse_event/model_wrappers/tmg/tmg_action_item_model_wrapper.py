from django.core.exceptions import ObjectDoesNotExist
from edc_action_item.model_wrappers import (
    ActionItemModelWrapper as BaseActionItemModelWrapper,
)
from edc_constants.constants import NEW

from ...get_ae_model import get_ae_model
from ..death_report_model_wrapper import DeathReportModelWrapper
from ..death_report_tmg_model_wrapper import DeathReportTmgModelWrapper


class TmgActionItemModelWrapper(BaseActionItemModelWrapper):
    def __init__(self, model_obj=None, **kwargs):
        self._death_report = None
        self._tmg_death_report = None
        super().__init__(model_obj=model_obj, **kwargs)

    @property
    def death_report_tmg_verbose_name(self):
        return self.death_report_tmg_model_cls._meta.verbose_name

    @property
    def death_report_model_cls(self):
        return get_ae_model("deathreport")

    @property
    def death_report_tmg_model_cls(self):
        return get_ae_model("deathreporttmg")

    @property
    def death_report(self):
        if not self._death_report:
            try:
                self._death_report = DeathReportModelWrapper(
                    model_obj=self.death_report_model_cls.objects.get(
                        subject_identifier=self.subject_identifier
                    )
                )
            except ObjectDoesNotExist:
                self._death_report = None
        return self._death_report

    def get_wrapped_tmg_death_report(self, tmg_death_report=None):
        if tmg_death_report:
            wrapped = DeathReportTmgModelWrapper(
                model_obj=self.death_report_tmg_model_cls.objects.get(
                    action_identifier=self.object.action_identifier,
                    death_report=self.death_report.object,
                )
            )
        else:
            wrapped = DeathReportTmgModelWrapper(
                model_obj=self.death_report_tmg_model_cls(
                    death_report=self.death_report.object,
                    subject_identifier=self.object.subject_identifier,
                    action_identifier=self.object.action_identifier,
                    parent_action_item=self.object.parent_action_item,
                    related_action_item=self.object.related_action_item,
                )
            )
        return wrapped

    @property
    def tmg_death_report(self):
        """Returns a wrapped new or existing Death Report TMG
        model instance.

        There can only be one instance per action item.
        """
        if not self._tmg_death_report:
            if self.death_report:
                if self.object.status == NEW:
                    self._tmg_death_report = self.get_wrapped_tmg_death_report()
                else:
                    model_obj = self.death_report_tmg_model_cls.objects.get(
                        action_identifier=self.object.action_identifier,
                        death_report=self.death_report.object,
                    )
                    self._tmg_death_report = self.get_wrapped_tmg_death_report(model_obj)
        return self._tmg_death_report
