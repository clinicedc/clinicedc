from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_action_item.models import ActionItem
from edc_model_wrapper import ModelWrapper

from ..constants import DEATH_REPORT_TMG_ACTION
from .death_report_tmg_model_wrapper import DeathReportTmgModelWrapper


class DeathReportModelWrapper(ModelWrapper):
    next_url_name = "tmg_death_listboard_url"
    model = f"{settings.ADVERSE_EVENT_APP_LABEL}.deathreport"
    next_url_attrs = ["subject_identifier"]

    @property
    def pk(self):
        return str(self.object.pk)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def death_report_tmg_model_cls(self):
        return django_apps.get_model(DeathReportTmgModelWrapper.model)

    @property
    def tmg_death_reports(self):
        objs = []
        for action_item in ActionItem.objects.filter(
            related_action_item=self.object.action_item,
            action_type__name=DEATH_REPORT_TMG_ACTION,
        ):
            try:
                objs.append(
                    DeathReportTmgModelWrapper(
                        model_obj=self.death_report_tmg_model_cls.objects.get(
                            action_identifier=action_item.action_identifier
                        )
                    )
                )
            except ObjectDoesNotExist:
                objs.append(
                    DeathReportTmgModelWrapper(
                        model_obj=self.death_report_tmg_model_cls(
                            death_report=self.object,
                            subject_identifier=self.object.subject_identifier,
                            action_identifier=action_item.action_identifier,
                            parent_action_item=action_item.parent_action_item,
                            related_action_item=action_item.related_action_item,
                        )
                    )
                )
        return objs
