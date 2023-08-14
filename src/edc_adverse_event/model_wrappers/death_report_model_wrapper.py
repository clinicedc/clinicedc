from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from edc_action_item.models import ActionItem
from edc_model_wrapper import ModelWrapper

from ..constants import DEATH_REPORT_TMG_ACTION
from ..utils import get_adverse_event_app_label, get_ae_model
from .death_report_tmg_model_wrapper import DeathReportTmgModelWrapper
from .death_report_tmg_second_model_wrapper import DeathReportTmgSecondModelWrapper

if TYPE_CHECKING:
    from ..model_mixins import DeathReportModelMixin


class DeathReportModelWrapper(ModelWrapper):
    next_url_name = "tmg_death_listboard_url"
    model = f"{get_adverse_event_app_label()}.deathreport"
    next_url_attrs = ["subject_identifier"]
    death_report_tmg_model_wrapper_cls = DeathReportTmgModelWrapper
    death_report_tmg_second_model_wrapper_cls = DeathReportTmgSecondModelWrapper

    def __init__(self, **kwargs):
        self._death_report_tmg = None
        self._death_report_tmg_second = None
        super().__init__(**kwargs)

    @property
    def pk(self):
        return str(self.object.id)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    def fix_action_item(self, action_item):
        action_item.related_action_item = self.object.action_item
        action_item.save()
        action_item.refresh_from_db()
        return action_item

    @property
    def tmg_death_reports(self):
        model_wrappers = []

        action_item = ActionItem.objects.get(action_identifier=self.object.action_identifier)
        # get tmg 1st
        opts = dict(
            subject_identifier=self.object.subject_identifier,
            parent_action_item=action_item,
            related_action_item=action_item.related_action_item,
            action_type__name=DEATH_REPORT_TMG_ACTION,
        )
        try:
            action_item = ActionItem.objects.get(**opts)
        except ObjectDoesNotExist:
            action_item = None
        except MultipleObjectsReturned as e:
            raise MultipleObjectsReturned(
                f"{e} See TMG action items for {self.object}. Options={opts}."
            )
        else:
            model_wrappers.append(self.get_death_report_tmg_model_wrapper(action_item))

        # get tmg second
        if action_item:
            opts = dict(
                subject_identifier=self.object.subject_identifier,
                parent_action_item=action_item,
                related_action_item=action_item.related_action_item,
                action_type__name=DEATH_REPORT_TMG_ACTION,
            )
            try:
                action_item = ActionItem.objects.get(**opts)
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned as e:
                raise MultipleObjectsReturned(
                    f"{e} See TMG action items for {self.object}. Options={opts}."
                )
            else:
                model_wrappers.append(
                    self.get_death_report_tmg_second_model_wrapper(action_item)
                )
        return model_wrappers

    @property
    def death_report_tmg_model_cls(self) -> Type[DeathReportModelMixin]:
        return get_ae_model("deathreporttmg")

    @property
    def death_report_tmg_second_model_cls(self) -> Type[DeathReportModelMixin]:
        return get_ae_model("deathreporttmgsecond")

    @property
    def death_report_tmg(self) -> DeathReportModelMixin:
        if not self._death_report_tmg:
            try:
                self._death_report_tmg = self.death_report_tmg_model_cls.objects.get(
                    subject_identifier=self.subject_identifier
                )
            except ObjectDoesNotExist:
                self._death_report_tmg = None
        return self._death_report_tmg

    @property
    def death_report_tmg_second(self) -> DeathReportModelMixin:
        if not self._death_report_tmg_second:
            try:
                self._death_report_tmg_second = (
                    self.death_report_tmg_second_model_cls.objects.get(
                        subject_identifier=self.subject_identifier
                    )
                )
            except ObjectDoesNotExist:
                self._death_report_tmg_second = None
        return self._death_report_tmg_second

    def get_death_report_tmg_model_wrapper(self, action_item):
        if not self.death_report_tmg:
            model_wrapper = self.death_report_tmg_model_wrapper_cls(
                model_obj=self.death_report_tmg_model_cls(
                    death_report=self.object,
                    subject_identifier=self.object.subject_identifier,
                    action_identifier=action_item.action_identifier,
                    parent_action_item=action_item.parent_action_item,
                    related_action_item=action_item.related_action_item,
                )
            )
        else:
            model_wrapper = self.death_report_tmg_model_wrapper_cls(
                model_obj=self.death_report_tmg
            )
        return model_wrapper

    def get_death_report_tmg_second_model_wrapper(self, action_item):
        if not self.death_report_tmg_second:
            model_wrapper = self.death_report_tmg_second_model_wrapper_cls(
                model_obj=self.death_report_tmg_model_cls(
                    death_report=self.object,
                    subject_identifier=self.object.subject_identifier,
                    action_identifier=action_item.action_identifier,
                    parent_action_item=action_item.parent_action_item,
                    related_action_item=action_item.related_action_item,
                )
            )
        else:
            model_wrapper = self.death_report_tmg_second_model_wrapper_cls(
                model_obj=self.death_report_tmg_second
            )
        return model_wrapper
